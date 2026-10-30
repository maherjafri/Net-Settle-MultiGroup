import json, os, threading, webbrowser, uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import storage
from expense_manager import money_to_paise, format_money
from reports import make_csv

ROOT=os.path.dirname(os.path.abspath(__file__))
UI_FILE=os.path.join(ROOT,"ui","index.html")
LOCK=threading.RLock()
MAX_BODY=128*1024

def state(data, active_id=None):
    groups=[]
    all_balances={}
    outstanding={}
    for g in data["groups"]:
        b=storage.group_balances(g)
        for m,v in b.items(): all_balances[m]=all_balances.get(m,0)+v
        plan=storage.ensure_plan(g)
        groups.append({"id":g["id"],"name":g["name"],"members":g["members"],
          "expenses":[{**e,"amount_text":format_money(e["amount"])} for e in reversed(g["expenses"])],
          "balances":[{"name":m,"paise":v,"text":format_money(abs(v)),"status":"owes" if v<0 else "receives" if v>0 else "settled"} for m,v in sorted(b.items())],
          "settlements":[{"id":s["id"],"from":s["from"],"to":s["to"],"amount":s["amount"],"amount_text":format_money(s["amount"]),"paid":bool(s.get("paid"))} for s in plan],
          "total_expense":sum(e["amount"] for e in g["expenses"]),
          "pending_total":sum(s["amount"] for s in plan if not s.get("paid")),
          "paid_count":sum(bool(s.get("paid")) for s in plan)})
    if not active_id or not any(g["id"]==active_id for g in groups): active_id=groups[0]["id"] if groups else None
    return {"members":sorted(set(data.get("members",[]))|set(m for g in data["groups"] for m in g["members"])),
      "groups":groups,"active_group_id":active_id,
      "overall":[{"name":m,"paise":v,"text":format_money(abs(v)),"status":"owes" if v<0 else "receives" if v>0 else "settled"} for m,v in sorted(all_balances.items())],
      "total_expense":sum(g["total_expense"] for g in groups)}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def send_body(self,code,body,ctype="application/json"):
        if not isinstance(body,(bytes,bytearray)): body=json.dumps(body,ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(body)
    def err(self,code,msg): self.send_body(code,{"error":msg})
    def body(self):
        length=int(self.headers.get("Content-Length","0"))
        if length>MAX_BODY: raise ValueError("Request too large.")
        try: d=json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError: raise ValueError("Invalid JSON.")
        if not isinstance(d,dict): raise ValueError("Invalid request.")
        return d
    def do_GET(self):
        u=urlparse(self.path)
        try:
            if u.path in ("/","/index.html"):
                with open(UI_FILE,"rb") as f: self.send_body(200,f.read(),"text/html; charset=utf-8"); return
            with LOCK:
                data=storage.load()
                if u.path=="/api/state":
                    active=parse_qs(u.query).get("group",[""])[0]
                    self.send_body(200,state(data,active)); return
                if u.path=="/api/report.csv":
                    self.send_body(200,make_csv(data).encode("utf-8-sig"),"text/csv; charset=utf-8"); return
            self.err(404,"Not found.")
        except (ValueError,OSError) as e: self.err(400,str(e))
    def do_POST(self):
        try:
            d=self.body()
            with LOCK:
                data=storage.load(); path=urlparse(self.path).path
                if path=="/api/groups":
                    name=str(d.get("name","")).strip()
                    if not name: raise ValueError("Enter a group name.")
                    g={"id":uuid.uuid4().hex,"name":name,"members":[],"expenses":[],"settlements":[]}
                    data["groups"].append(g); active=g["id"]
                elif path=="/api/members":
                    name=str(d.get("name","")).strip()
                    if not name: raise ValueError("Enter a member name.")
                    if name not in data["members"]: data["members"].append(name)
                    gid=str(d.get("group_id","")); g=storage.find_group(data,gid)
                    if name in g["members"]: raise ValueError("This member is already in the group.")
                    g["members"].append(name); active=gid
                elif path=="/api/expenses":
                    gid=str(d.get("group_id","")); g=storage.find_group(data,gid)
                    payer=str(d.get("payer","")).strip(); desc=str(d.get("description","")).strip()
                    cat=str(d.get("category","Other")).strip() or "Other"
                    people=d.get("participants")
                    if payer not in g["members"]: raise ValueError("Choose a payer from this group.")
                    if not isinstance(people,list): raise ValueError("Select participants.")
                    people=list(dict.fromkeys(str(x) for x in people))
                    if not people or any(x not in g["members"] for x in people): raise ValueError("Select valid group participants.")
                    if not desc: raise ValueError("Enter an expense description.")
                    amount=money_to_paise(d.get("amount",""))
                    g["expenses"].append({"id":uuid.uuid4().hex,"payer":payer,"amount":amount,"description":desc,"category":cat,"participants":people,"created_at":datetime.now().isoformat(timespec="seconds")})
                    # A changed ledger invalidates suggestions; never pretend old transfers are still current.
                    g["settlements"]=[]
                    active=gid
                elif path=="/api/settlements/paid":
                    gid=str(d.get("group_id","")); g=storage.find_group(data,gid)
                    storage.ensure_plan(g)
                    sid=str(d.get("settlement_id","")); s=next((x for x in g["settlements"] if x["id"]==sid),None)
                    if not s: raise ValueError("Settlement not found. Refresh the plan.")
                    s["paid"]=bool(d.get("paid")); active=gid
                elif path=="/api/settlements/recalculate":
                    gid=str(d.get("group_id","")); g=storage.find_group(data,gid)
                    storage.ensure_plan(g); active=gid
                elif path=="/api/groups/delete":
                    gid=str(d.get("group_id",""))
                    if len(data["groups"])<=1: raise ValueError("Keep at least one group.")
                    data["groups"]=[g for g in data["groups"] if g["id"]!=gid]
                    active=data["groups"][0]["id"]
                elif path=="/api/reset":
                    data=storage.empty_data(); active="default"
                else: self.err(404,"Not found."); return
                storage.save(data)
                self.send_body(200,state(data,active))
        except ValueError as e: self.err(400,str(e))
        except OSError as e: self.err(500,f"Storage error: {e}")

def run(port=8000,open_browser=True):
    httpd=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    url=f"http://127.0.0.1:{port}"
    print(f"Net-Settle running at {url} (Ctrl+C to stop)")
    if open_browser:
        import threading
        threading.Timer(.5,webbrowser.open,args=(url,)).start()
    try: httpd.serve_forever()
    except KeyboardInterrupt: print("\\nServer stopped.")
    finally: httpd.server_close()

if __name__=="__main__": run()
