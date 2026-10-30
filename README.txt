# SPENDWISE — Personal Expense Tracking System

## Requirements
- Windows with Python 3
- XAMPP with MySQL/MariaDB
- Python package `mysql-connector-python`

## Run it
1. Open XAMPP Control Panel.
2. Start **MySQL**. Apache is not required for this Tkinter desktop app.
3. Open Command Prompt in this folder and create a virtual environment:
   `py -m venv .venv`
4. Install the dependencies into it:
   `.venv\Scripts\python -m pip install -r requirements.txt`
5. Run the app with that environment:
   `.venv\Scripts\python main.py`
   In VS Code, select `.venv\Scripts\python.exe` as the Python interpreter.
6. By default the app connects to `localhost:3306`, username `root`, blank password.
   If your MySQL credentials differ, edit `DB_CONFIG` near the top of `main.py`.

The app automatically creates the `spendwise_db` database and its tables on first run.
You can also import `spendwise.sql` using phpMyAdmin (Import tab).

## Features
- Dashboard with income, expenses, category count, recent transactions, and category breakdown
- Add, archive, and delete transactions
- Restore archived transactions or permanently delete them from the Archive tab
- Filter transactions by Income/Expense and search descriptions/categories
- Add and delete categories

## Notes
- Currency is shown in Philippine pesos (₱).
- The app starts with default categories and no sample transactions.
- The figures in the provided PDF are reference/mockup figures; actual totals are calculated from database records.
- For a real multi-user deployment, add authentication and per-user records before use.
