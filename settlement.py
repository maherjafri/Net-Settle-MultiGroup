import heapq

class SettlementEngine:
    def __init__(self, balances): self.balances=dict(balances)
    def minimise_transfers(self):
        if sum(self.balances.values()) != 0:
            raise ValueError("Balances do not add up to zero.")
        debtors=[]; creditors=[]
        for name,balance in self.balances.items():
            if balance<0: heapq.heappush(debtors,(balance,name))
            elif balance>0: heapq.heappush(creditors,(-balance,name))
        result=[]
        while debtors and creditors:
            debt,name=heapq.heappop(debtors); credit,to=heapq.heappop(creditors)
            amount=min(-debt,-credit)
            result.append({"from":name,"to":to,"amount":amount})
            if -debt>amount: heapq.heappush(debtors,(debt+amount,name))
            if -credit>amount: heapq.heappush(creditors,(credit+amount,to))
        return result
    @staticmethod
    def estimate_fees(settlements, fee_per_transfer_paise):
        if fee_per_transfer_paise<0: raise ValueError("Fee cannot be negative.")
        return len(settlements)*fee_per_transfer_paise
