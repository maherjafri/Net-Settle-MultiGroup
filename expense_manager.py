from decimal import Decimal, InvalidOperation

def money_to_paise(value):
    try:
        amount = Decimal(str(value).strip())
        if not amount.is_finite() or amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        paise = amount * 100
        if paise != paise.to_integral_value():
            raise ValueError("Use at most two decimal places.")
        return int(paise)
    except (InvalidOperation, TypeError):
        raise ValueError("Enter a valid monetary amount.")

def format_money(paise):
    return f"₹{Decimal(int(paise))/100:,.2f}"

class ExpenseManager:
    """Compatibility facade for the original CLI; group logic lives in storage."""
    def __init__(self):
        self.members=set(); self.balances={}; self.expenses=[]; self.graph={}
    def add_member(self, name):
        name=name.strip()
        if not name: raise ValueError("Name cannot be empty.")
        if name in self.members: raise ValueError("This member already exists.")
        self.members.add(name); self.balances[name]=0; self.graph[name]=[]
    def add_expense(self,payer,amount_paise,description,category,participants):
        if payer not in self.members: raise ValueError("The payer is not registered.")
        participants=list(dict.fromkeys(participants))
        if not participants or any(p not in self.members for p in participants):
            raise ValueError("Select registered participants.")
        if amount_paise<=0: raise ValueError("Amount must be positive.")
        base,rem=divmod(amount_paise,len(participants))
        shares={p:base+(i<rem) for i,p in enumerate(participants)}
        self.balances[payer]+=amount_paise
        for p,share in shares.items(): self.balances[p]-=share
        self.expenses.append({"payer":payer,"amount":amount_paise,"description":description.strip(),
          "category":category.strip(),"participants":participants,"shares":shares})
    def total_expense(self): return sum(e["amount"] for e in self.expenses)
