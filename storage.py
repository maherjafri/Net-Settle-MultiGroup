"""Atomic JSON storage with migration from the original single-group format."""
import json, os, tempfile, threading, uuid
from datetime import datetime
from expense_manager import money_to_paise
DATA_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)), "netsettle_data.json")
LOCK=threading.RLock()

def empty_data():
    return {"version":2,"members":[],"groups":[{"id":"default","name":"My Group","members":[],"expenses":[],"settlements":[]} ]}

def _clean(data):
    # Migrate original format {members, expenses} into one group.
    if "groups" not in data:
        old_members=list(data.get("members",[]))
        group={"id":"default","name":"My Group","members":old_members,"expenses":[],"settlements":[]}
        for e in data.get("expenses",[]):
            group["expenses"].append({
                "id":uuid.uuid4().hex,"payer":e["payer"],"amount":int(e["amount"]),
                "description":e.get("description","Expense"),"category":e.get("category","Other"),
                "participants":list(e.get("participants",[])),
                "created_at":datetime.now().isoformat(timespec="seconds")
            })
        data={"version":2,"members":old_members,"groups":[group]}
    data.setdefault("version",2); data.setdefault("members",[]); data.setdefault("groups",[])
    for g in data["groups"]:
        g.setdefault("id",uuid.uuid4().hex); g.setdefault("name","Untitled group")
        g.setdefault("members",[]); g.setdefault("expenses",[]); g.setdefault("settlements",[])
        for e in g["expenses"]:
            e.setdefault("id",uuid.uuid4().hex); e.setdefault("created_at",datetime.now().isoformat(timespec="seconds"))
        for s in g["settlements"]:
            s.setdefault("id",uuid.uuid4().hex); s.setdefault("paid",False); s.setdefault("created_at",datetime.now().isoformat(timespec="seconds"))
    return data

def load(path=DATA_FILE):
    with LOCK:
        if not os.path.exists(path):
            data=empty_data(); save(data,path); return data
        try:
            with open(path,encoding="utf-8") as f: data=json.load(f)
            return _clean(data)
        except (OSError,ValueError,TypeError,KeyError) as exc:
            raise ValueError(f"Could not read saved data: {exc}")

def save(data,path=DATA_FILE):
    with LOCK:
        folder=os.path.dirname(os.path.abspath(path))
        fd,tmp=tempfile.mkstemp(prefix=".netsettle-",suffix=".tmp",dir=folder)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as f: json.dump(data,f,indent=2,ensure_ascii=False)
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp): os.remove(tmp)

def find_group(data,gid):
    g=next((x for x in data["groups"] if x["id"]==gid),None)
    if not g: raise ValueError("Group not found.")
    return g

def group_balances(group):
    balances={m:0 for m in group["members"]}
    for e in group["expenses"]:
        amount=int(e["amount"]); participants=e["participants"]
        if not participants: continue
        base,rem=divmod(amount,len(participants))
        for i,m in enumerate(participants): balances[m]-=base+(i<rem)
        balances[e["payer"]]+=amount
    return balances

def plan_for_group(group):
    from settlement import SettlementEngine
    balances=group_balances(group)
    # Only outstanding balances are used to generate a new plan. Paid transfers
    # are historical records and are not subtracted again from expense-derived balances.
    return SettlementEngine(balances).minimise_transfers()

def ensure_plan(group):
    """Refresh generated suggestions; retain paid status only when the same transfer remains."""
    old={(s["from"],s["to"],int(s["amount"])):bool(s.get("paid")) for s in group["settlements"]}
    fresh=plan_for_group(group)
    group["settlements"]=[{"id":uuid.uuid4().hex,"from":s["from"],"to":s["to"],"amount":s["amount"],
      "paid":old.get((s["from"],s["to"],s["amount"]),False),"created_at":datetime.now().isoformat(timespec="seconds")} for s in fresh]
    return group["settlements"]
