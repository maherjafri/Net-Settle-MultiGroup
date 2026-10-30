import csv
from expense_manager import format_money
from storage import group_balances, plan_for_group

def make_csv(data):
    import io
    out=io.StringIO(newline=""); w=csv.writer(out)
    w.writerow(["NET-SETTLE MULTI-GROUP REPORT"])
    for g in data["groups"]:
        w.writerow([]); w.writerow(["GROUP",g["name"]]); w.writerow(["Member","Net balance"])
        for name,b in sorted(group_balances(g).items()):
            w.writerow([name,format_money(b)])
        w.writerow([]); w.writerow(["EXPENSES"]); w.writerow(["Description","Category","Payer","Amount","Participants","Date"])
        for e in g["expenses"]:
            w.writerow([e["description"],e["category"],e["payer"],format_money(e["amount"]),", ".join(e["participants"]),e.get("created_at","")])
        w.writerow([]); w.writerow(["SETTLEMENT PLAN"]); w.writerow(["From","To","Amount","Status"])
        for s in g.get("settlements",[]):
            w.writerow([s["from"],s["to"],format_money(s["amount"]),"Paid" if s.get("paid") else "Pending"])
    return out.getvalue()
