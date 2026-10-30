Net-Settle --- Smart Multi-Group Expense Settlement
1. Project Overview
Net-Settle is a lightweight, local web application for recording
shared expenses and simplifying repayments between people.

It is designed for situations where people share expenses across
multiple groups, such as: - Roommates sharing rent, groceries, and
utility bills - Friends travelling together - Students managing college
trips or project expenses - People participating in more than one shared
group

A person can belong to multiple groups. Each group's expenses and
balances are calculated independently, so an expense in one group does
not silently cancel a debt in another group.

The application provides a browser-based dashboard, a Python backend,
and a JSON file for local data storage.
2. Problem Statement
When several people pay for shared expenses, manually calculating who
owes whom becomes confusing. The same person may pay for one expense,
owe money for another, and participate in multiple groups.

Traditional manual calculations can lead to: - Repeated or unnecessary
repayments - Incorrect expense splits - Confusion about who paid
upfront - Difficulty tracking completed and pending transfers - Mixing
expenses from unrelated groups

Net-Settle addresses this by maintaining group-wise expense records,
calculating each member's net balance, and generating a simplified
settlement plan.
3. Objectives
1. Record expenses shared by multiple people.
2. Maintain independent expense ledgers for multiple groups.
3. Allow members to participate in more than one group.
4. Calculate how much each member owes or should receive.
5. Reduce the number of suggested repayments using a greedy settlement
   algorithm.
6. Track whether a suggested transfer has been marked as paid.
7. Display an informational overall net position across groups.
8. Export expense and settlement information as a CSV report.
9. Store data locally without requiring an external database.
4. Main Features
4.1 Multiple Groups
Users can create separate groups for different activities, such as: -
Flatmates - Goa Trip - College Project - Office Lunch

Every group has its own members, expenses, balances, and settlement
plan.
4.2 Shared Members Across Groups
The same member can be added to multiple groups.

For example:

  Group 1   Group 2
  A         A
B         B
C         X
---       Y

Member A can participate in both groups, but the two groups' expense
records remain separate.
4.3 Expense Management
For every expense, the user can enter: - Person who paid upfront -
Expense amount - Description - Category - People sharing the expense

The application divides the amount equally among the selected
participants. If the amount cannot be divided evenly into paise, the
remaining paise are distributed one by one to the first participants in
the selected order.
4.4 Group-Wise Balance Calculation
The application calculates each member's net balance from the group's
expense records.
- A negative balance means the member owes money.
- A positive balance means the member should receive money.
- A zero balance means the member is settled.
The balance is calculated as:

Net Balance = Total Amount Paid − Total Share of Expenses

For each expense, the payer is credited with the full amount, and each
participant is debited by their share. If the payer is also a
participant, both operations apply to that member.
4.5 Settlement Plan
After expenses are recorded, the application can generate a settlement
plan.

The plan identifies: - Who needs to pay - Who should receive money - How
much should be transferred

The goal is to simplify repayments rather than having every member pay
every other member individually.
4.6 Payment Status
Each suggested transfer can be marked as: - Pending - Paid

The user can also undo a paid status.

Important: Payment status is a tracking record. Marking a transfer
as paid does not modify or delete the original expense records or
automatically change the expense-derived balances. The settlement plan
should be recalculated when the expense ledger changes.
4.7 Overall Personal Net Position
The dashboard also shows each person's combined net position across all
groups.

This is an informational summary only. It does not automatically cancel
or merge obligations between groups.

For example, if A owes B in one group and B owes A in another group,
both group-wise obligations remain visible in their respective groups.
4.8 CSV Report
Users can export a CSV report containing: - Group names - Member
balances - Expense descriptions and categories - Payers and
participants - Expense amounts and dates - Settlement transfers and
payment statuses
5. Technology Stack
  Technology                    Purpose
  Python                        Backend application logic
HTML                          Web page structure
CSS                           UI styling and responsive layout
JavaScript                    Frontend interaction and API communication
JSON                          Local data persistence
HTTP Server (http.server)   Serves the web application and API
heapq                       Priority queues used by the settlement algorithm
CSV module                    Generates downloadable reports

The project uses Python's standard library and does not require
third-party Python packages.
6. System Architecture
The application follows a simple frontend-backend-storage architecture.
                  USER
                   |
                   v
        Browser-based Web Interface
             HTML + CSS + JS
                   |
                   | HTTP requests
                   v
            Python Web Server
                server.py
                   |
          +--------+--------+
          |        |        |
          v        v        v
       Expense  Balance  Settlement
       Handling  Logic    Engine
          |        |        |
          +--------+--------+
                   |
                   v
             storage.py
                   |
                   v
          netsettle_data.json
                   |
                   v
              reports.py
                   |
                   v
              CSV Export
6.1 Frontend
The frontend is located in ui/index.html.

It provides: - Group navigation - Member management - Expense entry
forms - Participant selection - Split preview - Group balance display -
Settlement status controls - Expense history and search - Overall
net-position view - CSV export

JavaScript sends requests to the Python backend using the Fetch API and
updates the page using the returned JSON data.
6.2 Backend
The backend is implemented in server.py.

It: - Starts the local HTTP server - Serves the frontend page - Receives
frontend API requests - Validates incoming data - Calls the storage and
settlement logic - Returns JSON responses - Provides CSV downloads

The server binds to 127.0.0.1, so it is intended for local use on the
same computer.
6.3 Storage Layer
The storage.py module manages application data.

It is responsible for: - Creating the initial data structure - Loading
saved JSON data - Saving updates - Finding groups - Calculating group
balances - Generating settlement suggestions - Migrating older
single-group data into the multi-group structure

The JSON file is named netsettle_data.json.
6.4 Expense Manager
The expense_manager.py module contains monetary utility functions and
the ExpenseManager compatibility class.

It: - Validates monetary amounts - Converts rupees into paise - Formats
paise as rupee values - Provides basic expense and member handling
functionality

Amounts are stored as integer paise to avoid common floating-point
rounding errors.
6.5 Settlement Engine
The settlement.py module implements the settlement algorithm.

It uses Python's heapq priority queue to process debtors and
creditors.
6.6 Reports
The reports.py module creates CSV reports from the stored group data.
7. Settlement Algorithm
Net-Settle uses a greedy heap-based debt settlement algorithm.
Step 1: Calculate balances
The application calculates the net balance of every member in a group.

Example:

  Member     Net Balance
  A                -₹500
B                -₹300
C                +₹600
D                +₹200

Negative values represent debtors, while positive values represent
creditors.
Step 2: Separate debtors and creditors
The algorithm creates two priority queues: - Debtor heap: members with
negative balances - Creditor heap: members with positive balances
Step 3: Match the largest outstanding amounts
The algorithm repeatedly selects a debtor and a creditor and transfers
the smaller of their outstanding amounts.

For the example above:
1. A pays C ₹500.
2. B pays C ₹100.
3. B pays D ₹200.
The resulting plan contains three transfers.
Step 4: Continue until balances are cleared
After each transfer, the remaining balance of the debtor and creditor is
updated. Members whose balances reach zero are removed from further
processing.
Algorithm Complexity
Let n represent the number of members in a group.
- Heap construction and processing: O(n log n) time
- Auxiliary heap storage: O(n) space
Balance calculation takes O(E + P) time, where: - E is the number
of expenses - P is the total number of participant entries across
those expenses

Algorithm limitation: The greedy method is efficient, but it does
not guarantee the globally minimum possible number of transfers for
every balance configuration. It is used as a practical baseline in this
implementation.
8. Project Folder Structure
Net-Settle/
│
├── main.py
├── server.py
├── storage.py
├── expense_manager.py
├── settlement.py
├── reports.py
├── netsettle_data.json
├── README.md
│
└── ui/
    └── index.html
  File                                Responsibility
  main.py                           Application entry point and
command-line arguments

  server.py                         Local web server and API endpoints

  storage.py                        JSON persistence, group data, and
balance calculation

  expense_manager.py                Money validation, formatting, and
expense utilities

  settlement.py                     Greedy heap-based settlement
algorithm

  reports.py                        CSV report generation

  netsettle_data.json               Locally saved application data
ui/index.html                     Browser-based user interface
9. Installation and Execution
Requirements
- Python 3.8 or later
- A modern web browser
- No third-party Python packages are required
Step 1: Open the project folder
Open a terminal in the directory containing main.py.
Step 2: Run the application
python main.py
The server starts on:
http://127.0.0.1:8000
The application attempts to open the address in the default browser
automatically.
Step 3: Use a custom port (optional)
python main.py --port 9000
Then open:
http://127.0.0.1:9000
To prevent automatic browser opening:
python main.py --port 9000 --no-browser
Step 4: Stop the application
Return to the terminal and press:
Ctrl + C
10. Backend API Endpoints
The frontend communicates with the Python server through the following
endpoints.
  Method                  Endpoint                         Purpose
  GET                     /                              Serves the main UI

  GET                     /api/state                     Returns application and
group data

  GET                     /api/report.csv                Downloads the CSV
report

  POST                    /api/groups                    Creates a group

  POST                    /api/members                   Adds a member to a
group

  POST                    /api/expenses                  Records a new expense

  POST                    /api/settlements/paid          Updates a transfer's
paid status

  POST                    /api/settlements/recalculate   Recalculates a group's
settlement plan

  POST                    /api/groups/delete             Deletes a group
POST                    /api/reset                     Resets application data
POST requests use JSON request bodies. The server validates the data and
returns JSON responses.
11. Data Storage and Safety
All application data is stored locally in netsettle_data.json.

The storage layer uses a temporary file followed by an atomic
replacement when saving data. This helps reduce the risk of partially
written JSON files.

The application can migrate the original single-group data format into
the new multi-group structure.

Backup recommendation: Copy netsettle_data.json before resetting
the application or making major changes. Deleting this file removes the
locally stored application data.

The current server is designed for local use. It does not provide user
accounts, authentication, encrypted remote storage, or multi-device
synchronization.
12. Current Limitations and Future Scope
Current Limitations
- The settlement algorithm is greedy and is not guaranteed to find the
  global minimum number of transfers.
- The application runs locally and does not support remote multi-user
  access.
- There is no login or role-based access system.
- Expense splitting currently uses equal shares among selected
  participants.
- Payment status is tracked separately from the expense ledger.
- The overall net position is informational and does not settle debts
  across groups.
Possible Future Enhancements
1. Exact settlement optimisation: Compare the greedy approach with
   an exact or branch-and-bound approach for small groups.
2. Payment-aware optimisation: Incorporate already completed
   transfers into a formal settlement state.
3. Transaction costs: Allow a configurable fee per transfer and
   compare settlement plans by total cost.
4. Unequal expense splitting: Support custom shares and
   percentage-based splits.
5. Payment integration: Add payment links or supported
   payment-provider integrations.
6. User authentication: Add accounts and secure access for multiple
   users.
7. Visual analytics: Add spending charts, category breakdowns, and
   monthly trends.
8. Settlement history: Maintain an auditable record of generated
   plans and completed payments.
These are proposed extensions; they are not all implemented in the
current version.
13. Conclusion
Net-Settle provides a simple way to manage shared expenses across
multiple groups. It combines group-wise expense tracking, automatic
balance calculation, greedy settlement recommendations, payment-status
tracking, and CSV reporting in a local web application.

Its multi-group structure allows the same person to participate in
different groups without mixing their individual obligations. The
project also provides a foundation for future research into more
advanced debt-settlement optimisation techniques.
Project: Net-Settle --- Smart Multi-Group Expense Settlement
Primary language: Python
Interface: HTML, CSS, JavaScript
Storage: JSON
Execution: Local web application
