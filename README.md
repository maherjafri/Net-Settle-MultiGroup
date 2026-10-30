# Net-Settle 💸
### Smart Multi-Group Expense Settlement System

Net-Settle is a Python-based expense management application that simplifies shared expenses and repayments between people. It allows users to create multiple groups, record expenses, calculate individual balances, and generate optimised settlement suggestions using a greedy heap-based algorithm.

The application is designed to make group expense management easier, more transparent, and less time-consuming.

---

## 📌 Problem Statement

When multiple people share expenses, manually calculating who owes whom can become confusing. This becomes even more complicated when the same person participates in multiple groups.

Common challenges include:

- Tracking who paid for each expense.
- Calculating individual contributions.
- Identifying who owes money and who should receive it.
- Avoiding unnecessary transactions.
- Managing expenses across multiple groups without mixing their balances.
- Tracking completed and pending payments.

Net-Settle addresses these challenges through automated expense splitting, group-wise balance calculation, and settlement recommendations.

---

## 🎯 Objectives

- Manage shared expenses across multiple groups.
- Allow members to participate in multiple groups.
- Automatically calculate individual balances.
- Generate simplified repayment plans.
- Track paid and pending settlements.
- Display an overall personal net position across groups.
- Export expense and settlement records as CSV reports.
- Store application data locally using JSON.

---

## ✨ Features

### 1. Multi-Group Expense Management
- Create multiple groups for trips, roommates, projects, or other activities.
- Maintain separate expenses and balances for every group.
- Add the same member to different groups.
- Prevent unrelated group expenses from being mixed.

### 2. Expense Tracking
- Record the person who paid upfront.
- Enter expense amount and description.
- Categorise expenses such as Food, Travel, Rent, Shopping, and Utilities.
- Select members participating in an expense.
- Automatically divide expenses equally among selected participants.
- Preview the split before saving.

### 3. Automatic Balance Calculation

Net-Settle calculates the net balance of every member.

**Net Balance = Total Amount Paid − Total Share of Expenses**

- Positive balance: The member should receive money.
- Negative balance: The member owes money.
- Zero balance: The member is settled.

All monetary values are stored in paise to reduce floating-point rounding errors.

### 4. Smart Settlement Algorithm

The application uses a **Greedy Heap-Based Debt Settlement Algorithm** to simplify repayments.

Instead of requiring every member to pay everyone individually, the algorithm matches debtors with creditors and generates a smaller set of suggested transfers.

### 5. Payment Status Tracking
- Mark suggested transfers as Paid.
- Identify Pending transfers.
- Undo a paid status when required.
- View outstanding settlement amounts.

### 6. Overall Personal Net Position

View a combined net position for members participating in multiple groups.

This feature is informational only. Group-wise obligations remain separate and are not automatically cancelled against each other.

### 7. CSV Export

Export expense and settlement information for reporting, record keeping, and further analysis.

### 8. Responsive User Interface

A clean, light-themed dashboard built using HTML, CSS, and JavaScript.

---

## 🧠 Settlement Algorithm

Net-Settle implements a greedy heap-based settlement algorithm using Python's `heapq` module.

### How It Works

**Step 1: Calculate Individual Balances**

The application calculates the net balance of each member based on the expenses recorded in a group.

**Step 2: Separate Debtors and Creditors**

- Members with negative balances are treated as debtors.
- Members with positive balances are treated as creditors.

**Step 3: Match Debtors and Creditors**

The algorithm uses priority queues (heaps) to process outstanding balances.

**Step 4: Generate Transfers**

The smaller of the debtor's outstanding amount and creditor's outstanding amount is transferred.

**Step 5: Repeat**

The process continues until all possible balances are settled.

### Example

| Member | Net Balance |
|---|---:|
| A | -₹500 |
| B | -₹300 |
| C | +₹600 |
| D | +₹200 |

Generated settlement plan:

| From | To | Amount |
|---|---|---:|
| A | C | ₹500 |
| B | C | ₹100 |
| B | D | ₹200 |

The resulting plan simplifies the repayments into three transfers.

### Algorithm Complexity

For `n` members:

- **Time Complexity:** O(n log n)
- **Space Complexity:** O(n)

Balance calculation additionally depends on the number of expenses and participant entries.

**Note:** The current greedy algorithm is efficient, but it does not guarantee the globally minimum possible number of transactions for every balance configuration.

---

## 🏗️ System Architecture

The application follows a simple three-layer architecture.

```text
                  USER
                   |
                   v
        Browser-Based User Interface
             HTML + CSS + JS
                   |
                   | HTTP Requests
                   v
             Python Web Server
                 server.py
                   |
          +--------+--------+
          |        |        |
          v        v        v
       Expense   Balance  Settlement
       Manager   Logic     Engine
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
