"""
SPENDWISE - Personal Expense Tracking System
Python + Tkinter + XAMPP MariaDB/MySQL

Install:
    py -m pip install mysql-connector-python
Run:
    py main.py

Default XAMPP settings:
    host=localhost, user=root, password="", database=spendwise_db
Edit DB_CONFIG below if your MySQL credentials differ.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import calendar
from datetime import date, datetime
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Set your XAMPP MySQL password here, if you have one.
    "database": "spendwise_db",
    "port": 3306,
}

BG = "#FFF7F2"
SIDEBAR = "#FFF7F2"
SIDEBAR_ACTIVE = "#D2C5FF"
TEXT = "#050505"
MUTED = "#51465D"
WHITE = "#D2C5FF"
ACCENT = "#D2C5FF"
GREEN = "#286342"
RED = "#A83245"
BORDER = "#B9A9D8"
PRIMARY_BUTTON = "#5B347A"
PRIMARY_BUTTON_ACTIVE = "#482663"

DEFAULT_CATEGORIES = [
    ("Housing", "Expense"), ("Food", "Expense"), ("Transport", "Expense"),
    ("Utilities", "Expense"), ("Entertainment", "Expense"), ("Shopping", "Expense"),
    ("Health", "Expense"), ("Education", "Expense"), ("Other", "Expense"),
    ("Salary", "Income"), ("Allowance", "Income"), ("Freelance", "Income"),
]

class SpendwiseDB:
    def __init__(self):
        self.conn = None

    def connect(self):
        try:
            cfg = DB_CONFIG.copy()
            database = cfg.pop("database")
            self.conn = mysql.connector.connect(**cfg)
            cur = self.conn.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
            cur.close()
            self.conn.database = database
            self.setup()
            return True
        except Error as e:
            messagebox.showerror(
                "Database connection error",
                "Could not connect to XAMPP MySQL/MariaDB.\n\n"
                "1. Open XAMPP Control Panel and start MySQL.\n"
                "2. Check DB_CONFIG in main.py (host, port, username, password).\n\n"
                f"Details: {e}"
            )
            return False

    def setup(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(80) NOT NULL UNIQUE,
                type ENUM('Income','Expense') NOT NULL DEFAULT 'Expense'
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                transaction_date DATE NOT NULL,
                description VARCHAR(180) NOT NULL,
                category_id INT NULL,
                transaction_type ENUM('Income','Expense') NOT NULL DEFAULT 'Expense',
                amount DECIMAL(12,2) NOT NULL,
                archived TINYINT(1) NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_transaction_category
                    FOREIGN KEY (category_id) REFERENCES categories(category_id)
                    ON DELETE SET NULL
            )
        """)
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=DATABASE()
              AND TABLE_NAME='transactions'
              AND COLUMN_NAME='archived'
        """)
        if cur.fetchone()[0] == 0:
            cur.execute(
                "ALTER TABLE transactions "
                "ADD COLUMN archived TINYINT(1) NOT NULL DEFAULT 0"
            )
        cur.execute("""
            CREATE TABLE IF NOT EXISTS profile (
                profile_id INT PRIMARY KEY,
                full_name VARCHAR(120) NOT NULL DEFAULT 'Juan Dela Cruz',
                phone VARCHAR(30) DEFAULT '',
                birth_date DATE NULL
            )
        """)
        self.conn.commit()
        cur.execute("SELECT COUNT(*) FROM categories")
        if cur.fetchone()[0] == 0:
            cur.executemany("INSERT INTO categories (name, type) VALUES (%s,%s)", DEFAULT_CATEGORIES)
        cur.execute("SELECT COUNT(*) FROM profile")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO profile (profile_id, full_name, phone, birth_date) VALUES (1,%s,%s,%s)",
                ("Juan Dela Cruz", "09758496213", date(2003, 6, 20))
            )
        self.conn.commit()
        cur.close()

    def query(self, sql, params=(), fetch=True):
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            if fetch:
                return cur.fetchall()
            self.conn.commit()
            return cur.lastrowid
        finally:
            cur.close()

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()


class SpendwiseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SPENDWISE | Personal Expense Tracking System")
        self.geometry("1200x760")
        self.minsize(1000, 650)
        self.configure(bg=BG)
        self.db = SpendwiseDB()
        if not self.db.connect():
            self.after(100, self.destroy)
            return

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                             foreground=TEXT, rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background="#F0F3F8", foreground="#526078",
                             font=("Segoe UI", 9, "bold"), relief="flat")
        self.style.map("Treeview", background=[("selected", "#DCE7FF")],
                       foreground=[("selected", TEXT)])
        self.style.configure("TCombobox", padding=6)
        self.style.configure("TEntry", padding=7)

        self.active_page = "Dashboard"
        self.sidebar_buttons = {}
        self._build_shell()
        self.show_page("Dashboard")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="◈  SPENDWISE", bg=SIDEBAR, fg=TEXT,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=22, pady=(28, 4))
        tk.Label(self.sidebar, text="", bg=SIDEBAR, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=23, pady=(0, 36))

        for label, symbol in [
            ("Dashboard", "⌂"), ("Expenses", "↗"), ("Categories", "▦"), ("Archive", "▤")
        ]:
            btn = tk.Button(self.sidebar, text=f"   {symbol}    {label}", anchor="w",
                            command=lambda p=label: self.show_page(p), bd=0, relief="flat",
                            bg=SIDEBAR, fg="#000000", activebackground=SIDEBAR_ACTIVE,
                            activeforeground="#000000", font=("Segoe UI", 11), padx=12, pady=13,
                            cursor="hand2")
            btn.pack(fill="x", padx=12, pady=3)
            self.sidebar_buttons[label] = btn

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(30, 14))
        tk.Label(self.sidebar, text="PERSONAL FINANCE", bg=SIDEBAR, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=23)
        tk.Label(self.sidebar, text="SPENDWISE  •  v1.0", bg=SIDEBAR, fg=MUTED,
                 font=("Segoe UI", 8)).pack(side="bottom", anchor="w", padx=22, pady=20)

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        self.header = tk.Frame(self.main, bg=WHITE, height=76)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        self.page_title = tk.Label(self.header, text="Dashboard", bg=WHITE, fg=TEXT,
                                   font=("Segoe UI", 20, "bold"))
        self.page_title.pack(side="left", padx=30)
        self.date_label = tk.Label(self.header, text=date.today().strftime("%b %d, %Y"),
                                   bg=WHITE, fg=MUTED, font=("Segoe UI", 10))
        self.date_label.pack(side="right", padx=30)
        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=28, pady=24)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page(self, page):
        self.active_page = page
        self.page_title.config(text=page)
        for name, btn in self.sidebar_buttons.items():
            btn.config(bg=SIDEBAR_ACTIVE if name == page else SIDEBAR,
                       fg="#000000")
        self.clear_content()
        if page == "Dashboard":
            self.page_dashboard()
        elif page == "Expenses":
            self.page_expenses()
        elif page == "Categories":
            self.page_categories()
        elif page == "Archive":
            self.page_archive()

    def card(self, parent, title, value, subtitle="", color=ACCENT):
        frame = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        tk.Frame(frame, bg=color, height=4).pack(fill="x")
        inner = tk.Frame(frame, bg=WHITE)
        inner.pack(fill="both", expand=True, padx=18, pady=14)
        tk.Label(inner, text=title.upper(), bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(inner, text=value, bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(8, 3))
        if subtitle:
            tk.Label(inner, text=subtitle, bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w")
        return frame

    def money(self, amount):
        return f"₱{float(amount or 0):,.2f}"

    def totals(self):
        rows = self.db.query("""
            SELECT transaction_type, COALESCE(SUM(amount),0) AS total
            FROM transactions WHERE archived=0 GROUP BY transaction_type
        """)
        totals = {"Income": 0, "Expense": 0}
        for r in rows:
            totals[r["transaction_type"]] = float(r["total"])
        cats = self.db.query("SELECT COUNT(*) AS n FROM categories")[0]["n"]
        return totals, cats

    def page_dashboard(self):
        totals, cat_count = self.totals()
        tk.Label(self.content, text="Welcome back", bg=BG, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Here is a summary of your personal finances.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 18))

        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x")
        for i in range(3):
            cards.grid_columnconfigure(i, weight=1, uniform="cards")
        self.card(cards, "Total Income", self.money(totals["Income"]), "All recorded income", GREEN).grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.card(cards, "Total Spending", self.money(totals["Expense"]), "All recorded expenses", RED).grid(row=0, column=1, sticky="nsew", padx=5)
        self.card(cards, "Total Categories", str(cat_count), "Income and expense categories", ACCENT).grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        lower = tk.Frame(self.content, bg=BG)
        lower.pack(fill="both", expand=True, pady=(22, 0))
        left = tk.Frame(lower, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        right = tk.Frame(lower, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.panel_heading(left, "Recent Transactions", "View all", lambda: self.show_page("Expenses"))
        self.panel_heading(right, "Top Categories", "View all", lambda: self.show_page("Categories"))

        rows = self.db.query("""
            SELECT t.transaction_date, t.description, t.transaction_type, t.amount,
                   COALESCE(c.name,'Uncategorized') AS category
            FROM transactions t LEFT JOIN categories c ON c.category_id=t.category_id
            WHERE t.archived=0
            ORDER BY t.transaction_date DESC, t.transaction_id DESC LIMIT 7
        """)
        if not rows:
            tk.Label(left, text="No transactions yet. Add your first transaction in Expenses.",
                     bg=WHITE, fg=MUTED, font=("Segoe UI", 10), wraplength=420).pack(anchor="w", padx=18, pady=25)
        else:
            for r in rows:
                row = tk.Frame(left, bg=WHITE)
                row.pack(fill="x", padx=18, pady=9)
                tk.Label(row, text=r["description"], bg=WHITE, fg=TEXT,
                         font=("Segoe UI", 10, "bold")).pack(side="left", anchor="w")
                amount_color = GREEN if r["transaction_type"] == "Income" else TEXT
                sign = "+" if r["transaction_type"] == "Income" else "−"
                tk.Label(row, text=sign + self.money(r["amount"]), bg=WHITE, fg=amount_color,
                         font=("Segoe UI", 10, "bold")).pack(side="right")
                tk.Label(row, text=f'{r["category"]}  •  {r["transaction_date"]}', bg=WHITE,
                         fg=MUTED, font=("Segoe UI", 8)).pack(side="right", padx=12)

        cats = self.db.query("""
            SELECT c.name, COALESCE(SUM(t.amount),0) AS total
            FROM categories c LEFT JOIN transactions t
              ON t.category_id=c.category_id AND t.transaction_type='Expense' AND t.archived=0
            WHERE c.type='Expense'
            GROUP BY c.category_id, c.name
            HAVING total > 0
            ORDER BY total DESC LIMIT 6
        """)
        total_expense = totals["Expense"] or 0
        if not cats:
            tk.Label(right, text="Your category breakdown will appear here after you record expenses.",
                     bg=WHITE, fg=MUTED, font=("Segoe UI", 10), wraplength=380).pack(anchor="w", padx=18, pady=25)
        else:
            for c in cats:
                line = tk.Frame(right, bg=WHITE)
                line.pack(fill="x", padx=18, pady=(12, 2))
                tk.Label(line, text=c["name"], bg=WHITE, fg=TEXT,
                         font=("Segoe UI", 10, "bold")).pack(side="left")
                tk.Label(line, text=self.money(c["total"]), bg=WHITE, fg=TEXT,
                         font=("Segoe UI", 10)).pack(side="right")
                pct = float(c["total"]) / total_expense * 100 if total_expense else 0
                bar_bg = tk.Frame(right, bg="#EDF1F7", height=7)
                bar_bg.pack(fill="x", padx=18, pady=(5, 2))
                bar = tk.Frame(bar_bg, bg=ACCENT, height=7)
                bar.place(relx=0, rely=0, relheight=1, relwidth=min(pct/100, 1))
                tk.Label(right, text=f"{pct:.1f}% of total expenses", bg=WHITE, fg=MUTED,
                         font=("Segoe UI", 8)).pack(anchor="w", padx=18)

    def panel_heading(self, parent, title, link, command):
        head = tk.Frame(parent, bg=WHITE)
        head.pack(fill="x", padx=18, pady=(18, 8))
        tk.Label(head, text=title, bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Button(head, text=link, command=command, bg=WHITE, fg=ACCENT, bd=0,
                  font=("Segoe UI", 9, "bold"), cursor="hand2").pack(side="right")

    def page_expenses(self):
        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", pady=(0, 14))
        tk.Label(top, text="Manage your income and expenses.", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Button(top, text="+ Add Transaction", command=self.add_transaction,
                  bg=PRIMARY_BUTTON, fg="white", activebackground=PRIMARY_BUTTON_ACTIVE,
                  activeforeground="white",
                  bd=0, padx=16, pady=10, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(side="right")

        filterbar = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        filterbar.pack(fill="x", pady=(0, 12))
        tk.Label(filterbar, text="Type:", bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(14, 5), pady=10)
        self.exp_filter = ttk.Combobox(filterbar, values=["All", "Income", "Expense"], state="readonly", width=14)
        self.exp_filter.set("All")
        self.exp_filter.pack(side="left", padx=4, pady=8)
        tk.Label(filterbar, text="Search:", bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(15, 5))
        self.search_var = tk.StringVar()
        search = ttk.Entry(filterbar, textvariable=self.search_var, width=24)
        search.pack(side="left", padx=4, pady=8)
        tk.Button(filterbar, text="Apply", command=self.refresh_transactions,
                  bg=PRIMARY_BUTTON, fg="white", activebackground=PRIMARY_BUTTON_ACTIVE,
                  activeforeground="white", bd=0, padx=12, pady=7,
                  cursor="hand2").pack(side="left", padx=8)
        tk.Button(filterbar, text="Delete Selected", command=self.delete_transaction,
                  bg="#FDEBEC", fg=RED, bd=0, padx=12, pady=7, cursor="hand2").pack(side="right", padx=12)
        tk.Button(filterbar, text="Archive Selected", command=self.archive_selected_transactions,
                  bg=PRIMARY_BUTTON, fg="white", activebackground=PRIMARY_BUTTON_ACTIVE,
                  activeforeground="white", bd=0, padx=12, pady=7,
                  cursor="hand2").pack(side="right", padx=4)

        tablebox = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        tablebox.pack(fill="both", expand=True)
        cols = ("id", "date", "description", "category", "type", "amount")
        self.tx_tree = ttk.Treeview(tablebox, columns=cols, show="headings", selectmode="extended")
        headings = {"id":"ID", "date":"Date", "description":"Description", "category":"Category", "type":"Type", "amount":"Amount"}
        widths = {"id":55, "date":125, "description":280, "category":160, "type":100, "amount":140}
        for col in cols:
            self.tx_tree.heading(col, text=headings[col])
            self.tx_tree.column(col, width=widths[col], anchor="w" if col in ("description","category","type") else "center")
        self.tx_tree.column("amount", anchor="e")
        scrollbar = ttk.Scrollbar(tablebox, orient="vertical", command=self.tx_tree.yview)
        self.tx_tree.configure(yscrollcommand=scrollbar.set)
        self.tx_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        self.refresh_transactions()

    def refresh_transactions(self):
        if not hasattr(self, "tx_tree") or not self.tx_tree.winfo_exists():
            return
        for item in self.tx_tree.get_children():
            self.tx_tree.delete(item)
        kind = self.exp_filter.get() if hasattr(self, "exp_filter") else "All"
        search = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        sql = """
            SELECT t.transaction_id, t.transaction_date, t.description,
                   COALESCE(c.name,'Uncategorized') AS category, t.transaction_type, t.amount
            FROM transactions t LEFT JOIN categories c ON c.category_id=t.category_id
            WHERE t.archived=0
              AND (%s='All' OR t.transaction_type=%s)
              AND (t.description LIKE %s OR c.name LIKE %s)
            ORDER BY t.transaction_date DESC, t.transaction_id DESC
        """
        rows = self.db.query(sql, (kind, kind, f"%{search}%", f"%{search}%"))
        for r in rows:
            self.tx_tree.insert("", "end", values=(
                r["transaction_id"], r["transaction_date"], r["description"],
                r["category"], r["transaction_type"], self.money(r["amount"])
            ))

    def add_transaction(self):
        win = tk.Toplevel(self)
        win.title("Add Transaction")
        win.geometry("430x470")
        win.resizable(False, False)
        win.configure(bg=WHITE)
        win.transient(self)
        win.grab_set()
        tk.Label(win, text="Add Transaction", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(22, 16))
        form = tk.Frame(win, bg=WHITE)
        form.pack(fill="both", expand=True, padx=24)

        def field(label, widget):
            tk.Label(form, text=label, bg=WHITE, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 3))
            widget.pack(fill="x", pady=(0, 4))

        type_var = tk.StringVar(value="Expense")
        type_box = ttk.Combobox(form, textvariable=type_var, values=["Expense", "Income"], state="readonly")
        field("TRANSACTION TYPE", type_box)
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(form, textvariable=desc_var)
        field("DESCRIPTION", desc_entry)
        today = date.today()
        month_var = tk.StringVar(value=calendar.month_name[today.month])
        day_var = tk.StringVar(value=str(today.day))
        year_var = tk.StringVar(value=str(today.year))
        date_fields = tk.Frame(form, bg=WHITE)
        month_box = ttk.Combobox(
            date_fields, textvariable=month_var,
            values=[calendar.month_name[month] for month in range(1, 13)],
            state="readonly",
        )
        day_box = ttk.Combobox(date_fields, textvariable=day_var, state="readonly")
        year_box = ttk.Combobox(
            date_fields, textvariable=year_var,
            values=[str(year) for year in range(today.year - 100, today.year + 21)],
            state="readonly",
        )
        for box in (month_box, day_box, year_box):
            box.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def update_days(*_):
            month = list(calendar.month_name).index(month_var.get())
            year = int(year_var.get())
            days = [
                str(day)
                for day in range(1, calendar.monthrange(year, month)[1] + 1)
            ]
            day_box["values"] = days
            if day_var.get() not in days:
                day_var.set(days[-1])

        month_var.trace_add("write", update_days)
        year_var.trace_add("write", update_days)
        update_days()
        field("DATE", date_fields)
        cats = self.db.query("SELECT name FROM categories WHERE type=%s ORDER BY name", (type_var.get(),))
        cat_var = tk.StringVar()
        cat_box = ttk.Combobox(form, textvariable=cat_var, values=[c["name"] for c in cats], state="readonly")
        if cats:
            cat_box.set(cats[0]["name"])
        field("CATEGORY", cat_box)
        def update_categories():
            newcats = self.db.query("SELECT name FROM categories WHERE type=%s ORDER BY name", (type_var.get(),))
            cat_box["values"] = [c["name"] for c in newcats]
            cat_box.set(newcats[0]["name"] if newcats else "")
        type_box.bind("<<ComboboxSelected>>", lambda *_: update_categories())
        amount_var = tk.StringVar()
        field("AMOUNT (PHP)", ttk.Entry(form, textvariable=amount_var))

        def save():
            description = desc_var.get().strip()
            try:
                month = list(calendar.month_name).index(month_var.get())
                tx_date = date(int(year_var.get()), month, int(day_var.get()))
                amount = float(amount_var.get().replace(",", "").strip())
                if not description:
                    raise ValueError("Enter a description.")
                if amount <= 0:
                    raise ValueError("Amount must be greater than zero.")
                category = self.db.query("SELECT category_id FROM categories WHERE name=%s AND type=%s",
                                         (cat_var.get(), type_var.get()))
                category_id = category[0]["category_id"] if category else None
                self.db.query("""INSERT INTO transactions
                    (transaction_date, description, category_id, transaction_type, amount)
                    VALUES (%s,%s,%s,%s,%s)""",
                    (tx_date, description, category_id, type_var.get(), amount), fetch=False)
                win.destroy()
                self.show_page(self.active_page)
            except ValueError as e:
                messagebox.showwarning("Check transaction details", str(e), parent=win)
            except Error as e:
                messagebox.showerror("Database error", str(e), parent=win)

        tk.Button(win, text="Save Transaction", command=save, bg=PRIMARY_BUTTON, fg="white",
                  activebackground=PRIMARY_BUTTON_ACTIVE, activeforeground="white", bd=0, pady=11,
                  font=("Segoe UI", 10, "bold"), cursor="hand2").pack(fill="x", padx=24, pady=18)

    def delete_transaction(self):
        selected = self.tx_tree.selection()
        if not selected:
            messagebox.showinfo("Select transactions", "Please select transactions to delete.", parent=self)
            return
        if not messagebox.askyesno(
            "Confirm delete",
            "Permanently delete the selected transactions? This cannot be undone.",
            parent=self,
        ):
            return
        transaction_ids = [self.tx_tree.item(item, "values")[0] for item in selected]
        placeholders = ", ".join(["%s"] * len(transaction_ids))
        try:
            self.db.query(
                f"DELETE FROM transactions WHERE transaction_id IN ({placeholders})",
                tuple(transaction_ids),
                fetch=False,
            )
            self.refresh_transactions()
        except Error as e:
            messagebox.showerror("Could not delete transactions", str(e), parent=self)

    def page_archive(self):
        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", pady=(0, 14))
        tk.Label(top, text="Restore archived transactions or permanently delete them.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(side="left")
        tk.Button(top, text="Restore Selected", command=self.restore_archived_transactions,
                  bg=PRIMARY_BUTTON, fg="white", activebackground=PRIMARY_BUTTON_ACTIVE,
                  activeforeground="white", bd=0, padx=14, pady=9,
                  font=("Segoe UI", 10, "bold"), cursor="hand2").pack(side="right", padx=(8, 0))
        tk.Button(top, text="Delete Permanently", command=self.delete_archived_transactions,
                  bg="#FDEBEC", fg=RED, bd=0, padx=14, pady=9,
                  font=("Segoe UI", 10, "bold"), cursor="hand2").pack(side="right")

        box = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        box.pack(fill="both", expand=True)
        columns = ("id", "date", "description", "category", "type", "amount")
        self.archive_tree = ttk.Treeview(
            box, columns=columns, show="headings", selectmode="extended"
        )
        headings = {
            "id": "ID", "date": "Date", "description": "Description",
            "category": "Category", "type": "Type", "amount": "Amount",
        }
        widths = {
            "id": 55, "date": 125, "description": 280,
            "category": 160, "type": 100, "amount": 140,
        }
        for column in columns:
            self.archive_tree.heading(column, text=headings[column])
            self.archive_tree.column(
                column,
                width=widths[column],
                anchor="w" if column in ("description", "category", "type") else "center",
            )
        self.archive_tree.column("amount", anchor="e")
        scrollbar = ttk.Scrollbar(box, orient="vertical", command=self.archive_tree.yview)
        self.archive_tree.configure(yscrollcommand=scrollbar.set)
        self.archive_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        self.refresh_archived_transactions()

    def refresh_archived_transactions(self):
        if not hasattr(self, "archive_tree") or not self.archive_tree.winfo_exists():
            return
        for item in self.archive_tree.get_children():
            self.archive_tree.delete(item)
        try:
            rows = self.db.query("""
                SELECT t.transaction_id, t.transaction_date, t.description,
                       COALESCE(c.name, 'Uncategorized') AS category,
                       t.transaction_type, t.amount
                FROM transactions t
                LEFT JOIN categories c ON c.category_id=t.category_id
                WHERE t.archived=1
                ORDER BY t.transaction_date DESC, t.transaction_id DESC
            """)
            for row in rows:
                self.archive_tree.insert("", "end", values=(
                    row["transaction_id"], row["transaction_date"], row["description"],
                    row["category"], row["transaction_type"], self.money(row["amount"]),
                ))
        except Error as e:
            messagebox.showerror("Could not load archived transactions", str(e), parent=self)

    def archive_selected_transactions(self):
        selected = self.tx_tree.selection()
        if not selected:
            messagebox.showinfo("Select transactions", "Please select transactions to archive.", parent=self)
            return
        transaction_ids = [self.tx_tree.item(item, "values")[0] for item in selected]
        placeholders = ", ".join(["%s"] * len(transaction_ids))
        try:
            self.db.query(
                f"UPDATE transactions SET archived=1 "
                f"WHERE archived=0 AND transaction_id IN ({placeholders})",
                tuple(transaction_ids),
                fetch=False,
            )
            self.refresh_transactions()
        except Error as e:
            messagebox.showerror("Could not archive transactions", str(e), parent=self)

    def restore_archived_transactions(self):
        selected = self.archive_tree.selection()
        if not selected:
            messagebox.showinfo("Select transactions", "Please select transactions to restore.", parent=self)
            return
        transaction_ids = [self.archive_tree.item(item, "values")[0] for item in selected]
        placeholders = ", ".join(["%s"] * len(transaction_ids))
        try:
            self.db.query(
                f"UPDATE transactions SET archived=0 "
                f"WHERE archived=1 AND transaction_id IN ({placeholders})",
                tuple(transaction_ids),
                fetch=False,
            )
            self.refresh_archived_transactions()
        except Error as e:
            messagebox.showerror("Could not restore transactions", str(e), parent=self)

    def delete_archived_transactions(self):
        selected = self.archive_tree.selection()
        if not selected:
            messagebox.showinfo("Select transactions", "Please select transactions to delete.", parent=self)
            return
        if not messagebox.askyesno(
            "Delete archived transactions",
            "Permanently delete the selected transactions? This cannot be undone.",
            parent=self,
        ):
            return
        transaction_ids = [self.archive_tree.item(item, "values")[0] for item in selected]
        placeholders = ", ".join(["%s"] * len(transaction_ids))
        try:
            self.db.query(
                f"DELETE FROM transactions "
                f"WHERE archived=1 AND transaction_id IN ({placeholders})",
                tuple(transaction_ids),
                fetch=False,
            )
            self.refresh_archived_transactions()
        except Error as e:
            messagebox.showerror("Could not delete archived transactions", str(e), parent=self)

    def page_categories(self):
        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", pady=(0, 14))
        tk.Label(top, text="See where your money goes by category.", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Button(top, text="+ Add Category", command=self.add_category, bg=PRIMARY_BUTTON, fg="white",
                  activebackground=PRIMARY_BUTTON_ACTIVE, activeforeground="white",
                  bd=0, padx=16, pady=10, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(side="right")
        box = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        box.pack(fill="both", expand=True)
        cols = ("name", "type", "total", "percent")
        self.cat_tree = ttk.Treeview(box, columns=cols, show="headings")
        for col, title, width in [("name","Category",260),("type","Type",150),("total","Total Amount",200),("percent","% of Expenses",180)]:
            self.cat_tree.heading(col, text=title)
            self.cat_tree.column(col, width=width, anchor="w" if col in ("name","type") else "e")
        self.cat_tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.refresh_categories()
        actions = tk.Frame(self.content, bg=BG)
        actions.pack(fill="x", pady=(12, 0))
        tk.Button(actions, text="Delete Selected Category", command=self.delete_category,
                  bg="#FDEBEC", fg=RED, bd=0, padx=14, pady=9, cursor="hand2").pack(side="right")

    def refresh_categories(self):
        if not hasattr(self, "cat_tree") or not self.cat_tree.winfo_exists():
            return
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
        total = self.db.query(
            "SELECT COALESCE(SUM(amount),0) AS total FROM transactions "
            "WHERE transaction_type='Expense' AND archived=0"
        )[0]["total"]
        rows = self.db.query("""
            SELECT c.category_id,c.name,c.type,COALESCE(SUM(t.amount),0) AS total
            FROM categories c LEFT JOIN transactions t
              ON t.category_id=c.category_id AND t.archived=0
            GROUP BY c.category_id,c.name,c.type ORDER BY c.type,c.name
        """)
        for r in rows:
            pct = (float(r["total"])/float(total)*100) if total and r["type"] == "Expense" else 0
            self.cat_tree.insert("", "end", iid=str(r["category_id"]),
                                 values=(r["name"], r["type"], self.money(r["total"]), f"{pct:.1f}%"))

    def add_category(self):
        name = simpledialog.askstring("Add Category", "Category name:", parent=self)
        if not name or not name.strip():
            return
        kind = simpledialog.askstring("Category Type", "Type exactly Income or Expense:", initialvalue="Expense", parent=self)
        if not kind:
            return
        kind = kind.strip().title()
        if kind not in ("Income", "Expense"):
            messagebox.showwarning("Invalid type", "Type must be Income or Expense.")
            return
        try:
            self.db.query("INSERT INTO categories (name,type) VALUES (%s,%s)", (name.strip(), kind), fetch=False)
            self.show_page("Categories")
        except Error as e:
            messagebox.showerror("Could not add category", str(e))

    def delete_category(self):
        selected = self.cat_tree.selection()
        if not selected:
            messagebox.showinfo("Select a category", "Please select a category to delete.")
            return
        cat_id = selected[0]
        name = self.cat_tree.item(cat_id, "values")[0]
        if messagebox.askyesno("Delete category", f"Delete '{name}'? Existing transactions will become Uncategorized."):
            try:
                self.db.query("DELETE FROM categories WHERE category_id=%s", (cat_id,), fetch=False)
                self.show_page("Categories")
            except Error as e:
                messagebox.showerror("Could not delete category", str(e))

    def page_profile(self):
        profile = self.db.query("SELECT * FROM profile WHERE profile_id=1")[0]
        box = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        box.pack(fill="x", padx=60, pady=18)
        tk.Label(box, text="Personal Information", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=28, pady=(24, 4))
        tk.Label(box, text="Update the personal details connected to your account.", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=28, pady=(0, 18))
        form = tk.Frame(box, bg=WHITE)
        form.pack(fill="x", padx=28, pady=(0, 26))
        name_var = tk.StringVar(value=profile["full_name"] or "")
        phone_var = tk.StringVar(value=profile["phone"] or "")
        birth_var = tk.StringVar(value=profile["birth_date"].isoformat() if profile["birth_date"] else "")
        for label, var in [("FULL NAME", name_var), ("PHONE NUMBER", phone_var), ("DATE OF BIRTH (YYYY-MM-DD)", birth_var)]:
            tk.Label(form, text=label, bg=WHITE, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 4))
            ttk.Entry(form, textvariable=var).pack(fill="x", pady=(0, 4))

        def save_profile():
            try:
                birth = datetime.strptime(birth_var.get().strip(), "%Y-%m-%d").date() if birth_var.get().strip() else None
                if not name_var.get().strip():
                    raise ValueError("Full name cannot be empty.")
                self.db.query("""UPDATE profile SET full_name=%s, phone=%s, birth_date=%s
                                 WHERE profile_id=1""",
                              (name_var.get().strip(), phone_var.get().strip(), birth), fetch=False)
                messagebox.showinfo("Saved", "Your profile has been updated.")
            except ValueError as e:
                messagebox.showwarning("Check details", str(e))
            except Error as e:
                messagebox.showerror("Database error", str(e))
        tk.Button(form, text="Save Profile", command=save_profile, bg=PRIMARY_BUTTON, fg="white",
                  activebackground=PRIMARY_BUTTON_ACTIVE, activeforeground="white",
                  bd=0, padx=18, pady=10, font=("Segoe UI", 10, "bold"),
                  cursor="hand2").pack(anchor="w", pady=(20, 0))

    def on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = SpendwiseApp()
    app.mainloop()
