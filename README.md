# Net-Settle — Multi-Group Smart Expense Settlement

A minimal,local web app for shared expenses across multiple groups with overlapping members.

## Features
- Create independent groups (flatmates, trips, projects, etc.)
- Add members to each group; the same member can belong to multiple groups
- Record expenses, choose the upfront payer, and select participants
- Per-group balances and heap-based greedy settlement recommendations
- Mark a suggested transfer paid or pending
- Overall member net-position view across groups (informational only; group debts are never silently cancelled)
- CSV report covering groups, balances, expenses and settlement status
- JSON persistence and migration from the original single-group data file
- No third-party dependencies; local-only server

## Run
Python 3.8+:
```bash
python main.py --ui
```
Then visit http://127.0.0.1:8000

Optional:
```bash
python main.py --port 9000 --no-browser
```

## Important accounting behaviour
Group balances are calculated from the group's expense ledger. Settlement status is a record of whether a recommended transfer was reported complete; it does not change expense-derived balances. If an expense is added, the settlement plan is invalidated and should be recalculated. Paid flags are preserved only when a recalculated plan contains the exact same from/to/amount tuple. Overall balances are summed across groups for visibility only; they are not a legal or automatic cross-group netting instruction.

## Algorithm
Balance calculation: O(E + P), where E is number of expenses and P is the total number of participant entries. Settlement generation uses heaps and runs in O(n log n) time for n group members, with O(n) auxiliary space. Greedy settlement is efficient but does not guarantee the globally minimum number of transfers for every balance configuration.

## Data
`netsettle_data.json` is created next to `main.py`. Back up this file before experimenting with important data.
