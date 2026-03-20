# ============================================================
# GIAO DIỆN CHÍNH - DataSync Pro v3
# Sync POS Data (Pancake/POS pages.fm) → MariaDB (pos_db)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import json
from datetime import datetime

import config
import database as db_module
import sync_engine


# ──────────── THEME ────────────
class T:
    BG      = "#0d1117"
    BG2     = "#161b22"
    BG3     = "#21262d"
    ACCENT  = "#58a6ff"
    ACCENT2 = "#238636"
    RED     = "#f85149"
    ORANGE  = "#d29922"
    GREEN   = "#3fb950"
    TEXT    = "#e6edf3"
    SUBTEXT = "#8b949e"
    BORDER  = "#30363d"

    F_TITLE = ("Segoe UI", 16, "bold")
    F_HDR   = ("Segoe UI", 12, "bold")
    F_BODY  = ("Segoe UI", 10)
    F_MONO  = ("Consolas", 9)


# ──────────── MAIN APP ────────────
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("📦 DataSync Pro v3 — POS API → MariaDB")
        self.root.geometry("1180x820")
        self.root.minsize(950, 680)
        self.root.configure(bg=T.BG)

        self.is_syncing = False
        self.db = None
        self._current_stats = {}

        self._setup_styles()
        self._build_ui()
        self._load_config()

    # ── STYLES ────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TFrame", background=T.BG)
        s.configure("Card.TFrame", background=T.BG2)
        s.layout("Sync.Horizontal.TProgressbar",
            [('Horizontal.Progressbar.trough',
              {'sticky': 'nswe',
               'children': [('Horizontal.Progressbar.pbar',
                            {'side': 'left', 'sticky': 'ns'})]})])
        s.configure("Sync.Horizontal.TProgressbar",
            thickness=6, troughcolor=T.BG3, background=T.ACCENT)

    # ── BUILD UI ──────────────────────────────────────────────
    def _build_ui(self):
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self._build_title_bar()
        self._build_body()

    # ── TITLE BAR ─────────────────────────────────────────────
    def _build_title_bar(self):
        tb = tk.Frame(self.root, bg=T.BG2, height=52)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        tk.Label(tb, text="📦  DataSync Pro v3",
                 font=T.F_TITLE, fg=T.ACCENT, bg=T.BG2
        ).pack(side="left", padx=18, pady=8)
        tk.Label(tb, text="API → MariaDB (pos_db)",
                 font=T.F_BODY, fg=T.SUBTEXT, bg=T.BG2
        ).pack(side="left", padx=8, pady=8)
        self.db_status = tk.Label(tb, text="⚫  DB: Chưa kết nối",
                                  font=T.F_BODY, fg=T.RED, bg=T.BG2)
        self.db_status.pack(side="right", padx=18, pady=8)
        self.sync_status = tk.Label(tb, text="●  Sẵn sàng",
                                    font=T.F_BODY, fg=T.GREEN, bg=T.BG2)
        self.sync_status.pack(side="right", padx=10, pady=8)

    # ── BODY ─────────────────────────────────────────────────
    def _build_body(self):
        body = tk.Frame(self.root, bg=T.BG)
        body.pack(fill="both", expand=True, padx=10, pady=(6, 10))
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        self._build_left_panel(body)
        self._build_right_panel(body)

    # ── LEFT PANEL ────────────────────────────────────────────
    def _build_left_panel(self, parent):
        lp = tk.Frame(parent, bg=T.BG, width=380)
        lp.pack(side="left", fill="both", padx=(0, 8))
        lp.pack_propagate(False)

        self._card(lp, "🗄  Cấu hình Database").pack(fill="x", pady=(0, 6))
        self._db_config_card(lp).pack(fill="x", pady=(0, 8))

        self._card(lp, "🌐  Cấu hình API").pack(fill="x", pady=(0, 6))
        self._api_config_card(lp).pack(fill="x", pady=(0, 8))

        self._card(lp, "☑  Chọn dữ liệu đồng bộ").pack(fill="x", pady=(0, 6))
        self._data_selection_card(lp).pack(fill="x", pady=(0, 8))

        self._card(lp, "⚙  Tùy chọn").pack(fill="x", pady=(0, 6))
        self._options_card(lp).pack(fill="x", pady=(0, 8))

        tk.Button(lp, text="💾  Lưu toàn bộ cấu hình",
                  command=self._save_all,
                  bg=T.ACCENT2, fg="white", relief="flat", bd=0,
                  font=T.F_BODY, cursor="hand2", padx=15, pady=9
        ).pack(fill="x", pady=(4, 0))

    # ── RIGHT PANEL ───────────────────────────────────────────
    def _build_right_panel(self, parent):
        rp = tk.Frame(parent, bg=T.BG)
        rp.pack(side="right", fill="both", expand=True)
        rp.columnconfigure(0, weight=1)

        # Action buttons
        act = tk.Frame(rp, bg=T.BG)
        act.pack(fill="x", pady=(0, 8))

        self.btn_sync = tk.Button(act,
            text="▶  BẮT ĐẦU ĐỒNG BỘ",
            command=self._start_sync,
            bg=T.ACCENT, fg="white", relief="flat",
            font=("Segoe UI", 12, "bold"), cursor="hand2", padx=22, pady=10)
        self.btn_sync.pack(side="left")

        self.btn_stop = tk.Button(act,
            text="■  DỪNG LẠI",
            command=self._stop_sync, state="disabled",
            bg=T.RED, fg="white", relief="flat",
            font=("Segoe UI", 11, "bold"), cursor="hand2", padx=14, pady=10)
        self.btn_stop.pack(side="left", padx=(5, 0))

        tk.Button(act, text="🗑  Xóa Log",
            command=self._clear_log,
            bg=T.BG3, fg=T.TEXT, relief="flat", font=T.F_BODY,
            cursor="hand2", padx=12, pady=10
        ).pack(side="right")

        tk.Button(act, text="📋  Export",
            command=self._export_log,
            bg=T.BG3, fg=T.TEXT, relief="flat", font=T.F_BODY,
            cursor="hand2", padx=12, pady=10
        ).pack(side="right", padx=(5, 0))

        # Progress
        self._card(rp, "📊  Tiến trình đồng bộ").pack(fill="x", pady=(0, 6))
        self._progress_card(rp).pack(fill="x", pady=(0, 10))

        # Log
        tk.Label(rp, text="📋  Nhật ký",
                 font=T.F_HDR, fg=T.TEXT, bg=T.BG
        ).pack(anchor="w", pady=(2, 4))

        self.log = scrolledtext.ScrolledText(rp,
            font=T.F_MONO, bg=T.BG2, fg="#d4d4d4",
            insertbackground=T.ACCENT, relief="flat", bd=0,
            wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True)
        self._setup_log_tags()

        self._log("HEADER", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._log("HEADER", "  DataSync Pro v2 — Sẵn sàng đồng bộ")
        self._log("INFO",   "  Kết nối DB → Nhập API → Chọn data → Sync")
        self._log("HEADER", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # ── DB CONFIG CARD ────────────────────────────────────────
    def _db_config_card(self, parent):
        f = tk.Frame(parent, bg=T.BG2)

        fields = [
            ("host",     "Host:",     config.DB_CONFIG.get("host",     "100.70.133.122")),
            ("port",     "Port:",     str(config.DB_CONFIG.get("port",  3306))),
            ("database", "Database:", config.DB_CONFIG.get("database", "pos_db")),
            ("user",     "User:",     config.DB_CONFIG.get("user",     "root")),
        ]

        self._db_entries = {}
        for key, label, default in fields:
            row = tk.Frame(f, bg=T.BG2)
            row.pack(fill="x", padx=14, pady=3)
            tk.Label(row, text=label, bg=T.BG2, fg=T.SUBTEXT,
                     font=T.F_BODY, width=10, anchor="w"
            ).pack(side="left")
            ent = tk.Entry(row, font=T.F_BODY, bg=T.BG3,
                           fg=T.TEXT, insertbackground=T.TEXT, relief="flat", bd=0)
            ent.insert(0, default)
            ent.pack(side="left", fill="x", expand=True)
            self._db_entries[key] = ent

        # Password row
        pw_row = tk.Frame(f, bg=T.BG2)
        pw_row.pack(fill="x", padx=14, pady=3)
        tk.Label(pw_row, text="Password:", bg=T.BG2, fg=T.SUBTEXT,
                 font=T.F_BODY, width=10, anchor="w"
        ).pack(side="left")
        self._db_entries["password"] = tk.Entry(pw_row, font=T.F_BODY, bg=T.BG3,
                   fg=T.TEXT, insertbackground=T.TEXT, relief="flat", bd=0, show="●")
        self._db_entries["password"].insert(0, config.DB_CONFIG.get("password", ""))
        self._db_entries["password"].pack(side="left", fill="x", expand=True)

        # Test button
        btn_row = tk.Frame(f, bg=T.BG2)
        btn_row.pack(fill="x", padx=14, pady=(6, 10))
        tk.Button(btn_row, text="🔗  Test kết nối",
            command=self._test_db_connection,
            bg=T.BG3, fg=T.TEXT, relief="flat", font=T.F_BODY,
            cursor="hand2", padx=10, pady=5
        ).pack(side="left")

        return f

    # ── API CONFIG CARD ────────────────────────────────────────
    def _api_config_card(self, parent):
        f = tk.Frame(parent, bg=T.BG2)

        tk.Label(f, text="Base URL:", bg=T.BG2, fg=T.SUBTEXT,
                 font=T.F_BODY, anchor="w"
        ).pack(fill="x", padx=14, pady=(10, 2))

        self._api_url = tk.Entry(f, font=T.F_BODY, bg=T.BG3,
            fg=T.TEXT, insertbackground=T.TEXT, relief="flat", bd=0)
        self._api_url.pack(fill="x", padx=14, pady=(0, 8))

        tk.Label(f, text="Headers (JSON - tùy chọn):", bg=T.BG2, fg=T.SUBTEXT,
                 font=T.F_BODY, anchor="w"
        ).pack(fill="x", padx=14, pady=(0, 2))

        hdrs = tk.Frame(f, bg=T.BG2)
        hdrs.pack(fill="x", padx=14, pady=(0, 10))
        self._api_headers = tk.Text(hdrs, font=T.F_MONO, height=4,
            bg=T.BG3, fg=T.TEXT, insertbackground=T.TEXT,
            relief="flat", bd=0, wrap="word")
        self._api_headers.pack(fill="x")

        return f

    # ── DATA SELECTION CARD ────────────────────────────────────
    def _data_selection_card(self, parent):
        f = tk.Frame(parent, bg=T.BG2)

        entities = [
            ("variations",    "🔀  Variations",    "Biến thể SP"),
            ("products",       "📦  Products",      "Sản phẩm"),
            ("customers",     "👤  Customers",     "Khách hàng"),
            ("orders",        "🧾  Orders",         "Đơn hàng"),
            ("warehouses",    "🏭  Warehouses",     "Kho hàng"),
            ("categories",    "📂  Categories",    "Danh mục SP"),
            ("tags",          "🏷  Tags",           "Nhãn đơn"),
            ("order_sources", "🌐  Order Sources", "Nguồn đơn"),
            ("users",         "👥  Users",          "Nhân viên"),
        ]

        self._entity_vars = {}
        for key, label, desc in entities:
            row = tk.Frame(f, bg=T.BG2)
            row.pack(fill="x", padx=14, pady=5)
            var = tk.BooleanVar(
                value=config.SYNC_CONFIG.get(key, {}).get("enabled", True))
            self._entity_vars[key] = var
            tk.Checkbutton(row, variable=var, onvalue=True, offvalue=False,
                bg=T.BG2, activebackground=T.BG2, fg=T.ACCENT, selectcolor=T.BG3,
                activeforeground=T.ACCENT, cursor="hand2",
                highlightthickness=0, bd=0
            ).pack(side="left")
            tk.Label(row, text=label, bg=T.BG2, fg=T.TEXT,
                     font=T.F_HDR, anchor="w"
            ).pack(side="left", padx=(5, 0))
            tk.Label(row, text=desc, bg=T.BG2, fg=T.SUBTEXT,
                     font=("Segoe UI", 8), anchor="e"
            ).pack(side="right")

        return f

    # ── OPTIONS CARD ───────────────────────────────────────────
    def _options_card(self, parent):
        f = tk.Frame(parent, bg=T.BG2)
        row = tk.Frame(f, bg=T.BG2)
        row.pack(fill="x", padx=14, pady=8)
        tk.Label(row, text="Chế độ:", bg=T.BG2, fg=T.SUBTEXT,
                 font=T.F_BODY
        ).pack(side="left")
        self._sync_mode = tk.StringVar(value="full")
        for val, txt in [("full", "Full Sync"), ("incremental", "Incremental")]:
            tk.Radiobutton(row, text=txt, variable=self._sync_mode, value=val,
                bg=T.BG2, fg=T.TEXT, selectcolor=T.BG3,
                activebackground=T.BG2, activeforeground=T.ACCENT,
                font=T.F_BODY, cursor="hand2", indicatoron=0, width=11, bd=0
            ).pack(side="right", padx=(5, 0))
        return f

    # ── PROGRESS CARD ──────────────────────────────────────────
    def _progress_card(self, parent):
        f = tk.Frame(parent, bg=T.BG2)

        entities = [
            ("variations",    "Variations"),
            ("products",       "Products"),
            ("customers",     "Customers"),
            ("orders",        "Orders"),
            ("warehouses",    "Warehouses"),
            ("categories",    "Categories"),
            ("tags",          "Tags"),
            ("order_sources", "Order Sources"),
            ("users",         "Users"),
            ("addresses",     "Addresses"),
        ]

        self._pb = {}
        self._pb_lbl = {}
        self._pb_sub = {}

        for key, label in entities:
            row = tk.Frame(f, bg=T.BG2)
            row.pack(fill="x", padx=14, pady=3)
            hdr = tk.Frame(row, bg=T.BG2)
            hdr.pack(fill="x")
            self._pb_lbl[key] = tk.Label(hdr,
                text=f"{label}: --", font=T.F_BODY, bg=T.BG2, fg=T.SUBTEXT, anchor="w")
            self._pb_lbl[key].pack(side="left")
            self._pb_sub[key] = tk.Label(hdr, text="",
                font=("Segoe UI", 8), bg=T.BG2, fg=T.SUBTEXT, anchor="e")
            self._pb_sub[key].pack(side="right")
            pb = ttk.Progressbar(row, length=100, mode="determinate",
                                  style="Sync.Horizontal.TProgressbar")
            pb.pack(fill="x", pady=(2, 6))
            self._pb[key] = pb

        return f

    # ── CARD HELPER ────────────────────────────────────────────
    def _card(self, parent, title):
        f = tk.Frame(parent, bg=T.BG2)
        tk.Label(f, text=title, font=T.F_HDR, fg=T.ACCENT,
                 bg=T.BG2, anchor="w"
        ).pack(fill="x", padx=15, pady=(10, 4))
        tk.Frame(f, bg=T.BORDER, height=1).pack(fill="x", padx=15)
        return f

    # ── LOG TAGS ───────────────────────────────────────────────
    def _setup_log_tags(self):
        self.log.tag_config("INFO",    foreground="#58a6ff")
        self.log.tag_config("SUCCESS", foreground="#3fb950")
        self.log.tag_config("WARNING", foreground="#d29922")
        self.log.tag_config("ERROR",   foreground="#f85149")
        self.log.tag_config("HEADER",  foreground=T.ACCENT,
                               font=("Consolas", 10, "bold"))
        self.log.tag_config("DATA",    foreground="#c9c9c9")

    # ── LOG ────────────────────────────────────────────────────
    def _log(self, level, msg):
        self.log.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.insert("end", f"[{ts}] {msg}\n", level)
        self.log.see("end")
        self.log.configure(state="disabled")
        lines = int(self.log.index("end - 1 line").split(".")[0])
        if lines > config.MAX_LOG_LINES:
            self.log.configure(state="normal")
            self.log.delete("1.0", f"{lines - config.MAX_LOG_LINES + 20}.0")
            self.log.configure(state="disabled")

    # ── LOAD CONFIG ────────────────────────────────────────────
    def _load_config(self):
        self._api_url.insert(0, config.API_CONFIG.get("base_url", ""))
        if config.API_CONFIG.get("headers"):
            self._api_headers.insert("1.0",
                json.dumps(config.API_CONFIG["headers"], indent=2))
        for k, ent in self._db_entries.items():
            val = config.DB_CONFIG.get(k, "")
            ent.delete(0, "end")
            ent.insert(0, val)

    # ── SAVE ALL ───────────────────────────────────────────────
    def _save_all(self):
        port_val = self._db_entries["port"].get().strip()
        config.DB_CONFIG["port"] = int(port_val) if port_val else 3306
        config.DB_CONFIG["host"] = self._db_entries["host"].get().strip()
        config.DB_CONFIG["database"] = self._db_entries["database"].get().strip()
        config.DB_CONFIG["user"] = self._db_entries["user"].get().strip()
        config.DB_CONFIG["password"] = self._db_entries["password"].get()
        config.API_CONFIG["base_url"] = self._api_url.get().strip()
        try:
            hdrs = self._api_headers.get("1.0", "end").strip()
            config.API_CONFIG["headers"] = json.loads(hdrs) if hdrs else {}
        except json.JSONDecodeError:
            messagebox.showerror("Lỗi", "Headers phải là JSON hợp lệ!")
            return
        for k, var in self._entity_vars.items():
            if k not in config.SYNC_CONFIG:
                config.SYNC_CONFIG[k] = {"enabled": True, "last_sync": None}
            config.SYNC_CONFIG[k]["enabled"] = var.get()
        self._log("SUCCESS", "✓ Đã lưu toàn bộ cấu hình!")

    # ── TEST DB ────────────────────────────────────────────────
    def _test_db_connection(self):
        host = self._db_entries["host"].get().strip()
        port = int(self._db_entries["port"].get().strip() or 3306)
        user = self._db_entries["user"].get().strip()
        pw   = self._db_entries["password"].get()
        db   = self._db_entries["database"].get().strip()

        self._log("INFO", f"Đang kết nối {host}:{port}/{db}...")

        try:
            import mariadb
            tmp_conn = mariadb.connect(
                host=host, port=port, user=user, password=pw,
                database=db, connect_timeout=10)
            cur = tmp_conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
            tmp_conn.close()
            self._log("SUCCESS", f"✓ Kết nối DB thành công! ({db})")
            self._update_db_status("connected")
        except Exception as ex:
            self._log("ERROR", f"✗ Lỗi kết nối: {ex}")
            self._update_db_status("disconnected")

    def _update_db_status(self, state):
        def _inner():
            if state == "connected":
                self.db_status.config(text="🟢  DB: Đã kết nối", fg=T.GREEN)
            else:
                self.db_status.config(text="⚫  DB: Chưa kết nối", fg=T.RED)
        self.root.after(0, _inner)

    # ── SYNC ──────────────────────────────────────────────────
    def _start_sync(self):
        if self.is_syncing:
            messagebox.showinfo("Đang chạy", "Có tiến trình đang chạy!")
            return
        base_url = self._api_url.get().strip().rstrip("/")
        if not base_url:
            messagebox.showwarning("Cảnh báo", "Nhập Base URL của API!")
            return
        selected = [k for k, v in self._entity_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("Cảnh báo", "Chọn ít nhất 1 loại dữ liệu!")
            return
        self._save_all()
        self.is_syncing = True
        self._sync_state(True)
        self._current_stats = {}
        for key in self._pb:
            self._pb[key]["value"] = 0
            self._pb_lbl[key].config(
                text=f"{key.replace('_',' ').title()}: --", fg=T.SUBTEXT)
            self._pb_sub[key].config(text="")
        thread = threading.Thread(target=self._sync_worker,
                                 args=(selected,), daemon=True)
        thread.start()

    def _sync_worker(self, selected):
        import api_client as api_module

        base_url = self._api_url.get().strip().rstrip("/")
        mode = self._sync_mode.get()

        # Connect DB
        try:
            self.db = db_module.Database()
            self._update_db_status("connected")
            self._log("INFO", "🟢 Kết nối DB thành công")
        except Exception as ex:
            self._log("ERROR", f"✗ Không thể kết nối DB: {ex}")
            self._on_sync_done()
            return

        self._log("HEADER", f"━━━ BẮT ĐẦU SYNC [{mode.upper()}] ━━━")
        self._log("INFO",   f"  API: {base_url}")
        self._log("INFO",   f"  Entities: {', '.join(selected)}")

        # Sync order (respect FK): variations → products → customers → orders → ...
        sync_order = ["variations", "products", "customers", "orders", "warehouses",
                      "categories", "tags", "order_sources", "users"]
        to_sync = [e for e in sync_order if e in selected]

        # Temporary buffers for nested data
        all_addresses = {}     # extracted from customers API
        all_order_items = {}   # extracted from order detail
        all_payments = {}      # extracted from order detail
        all_products = {}      # extracted from variations API

        api = api_module.ApiClient()
        api.base_url = base_url  # override from GUI input

        for idx, entity in enumerate(to_sync):
            self._set_progress(entity, 0, "Đang bắt đầu...", T.SUBTEXT)
            fm = sync_engine.FIELD_MAPS[entity]
            table = fm["table"]

            self._log("INFO", f"\n→ [{idx+1}/{len(to_sync)}] "
                              f"SYNC: {entity.upper()} → {table}")
            self._set_progress(entity, 5, "Đang gọi API...", T.SUBTEXT)

            try:
                endpoint, paginated = config.ENDPOINTS.get(entity, (f"/{entity}", False))

                if entity == "orders":
                    # ── TWO-PHASE: list orders → fetch each detail ──
                    ck = config.get_checkpoint(entity)
                    resume_from = ck.get("page", 0) + 1
                    if resume_from > 1:
                        self._log("INFO", f"  → Resuming from page {resume_from} (checkpoint found)")

                    self._log("INFO", "  📋 Phase 1: Fetching order list...")
                    order_ids = []

                    def collect_ids(page_data):
                        for o in page_data:
                            oid = sync_engine._get_nested(o, "id")
                            if oid:
                                order_ids.append(oid)

                    def on_progress_orders(page, total_pages, cnt, tot):
                        config.save_checkpoint(entity, page, total_pages, tot)
                        self._log("INFO", f"  Page {page}/{total_pages} — {tot} orders found")

                    api.fetch_pages(endpoint, on_page=collect_ids,
                        on_progress=on_progress_orders,
                        stop_check=lambda: False, delay=0.05,
                        resume_from=resume_from)
                    total_orders = len(order_ids)
                    self._log("INFO", f"  → {total_orders} orders to fetch")

                    if total_orders == 0:
                        self._set_progress(entity, 100, "✓ 0 orders", T.GREEN)
                        continue

                    self._log("INFO", "  📦 Phase 2: Fetching order details...")

                    def on_order_detail(detail):
                        # Extract nested data from order detail (items + payments only)
                        # NOTE: customers/addresses come from separate customer API
                        cust, addr, items, pays = \
                            sync_engine.extract_from_order_detail(detail)
                        for item in items:
                            iid = item.get("id")
                            if iid:
                                all_order_items[iid] = item
                        for pay in pays:
                            pid = pay.get("id")
                            if pid:
                                all_payments[pid] = pay
                        # Upsert order itself
                        rows = sync_engine.transform_batch([detail], entity)
                        if rows:
                            self.db.upsert_batches(
                                table, rows,
                                batch_size=config.BATCH_INSERT)

                    def on_progress_fetch(i, total):
                        pct = int(i * 100 / total)
                        self._set_progress(entity, pct,
                            f"Detail {i}/{total}...", T.SUBTEXT)
                        if i % 100 == 0:
                            self._log("INFO", f"  Fetched {i}/{total} order details")

                    api.fetch_order_details(order_ids,
                        on_order=on_order_detail,
                        on_progress=on_progress_fetch,
                        stop_check=lambda: False, delay=0.05)

                    self._log("SUCCESS",
                        f"  ✓ Orders synced — "
                        f"{len(all_addresses)} addresses, "
                        f"{len(all_order_items)} items, "
                        f"{len(all_payments)} payments buffered")

                    self._set_progress(entity, 100, f"✓ {total_orders} orders", T.GREEN)

                elif entity == "products":
                    # ── PRODUCTS: upsert products extracted from variations ──
                    self._log("INFO", f"  📦 Upserting {len(all_products)} products...")
                    if all_products:
                        prod_rows = list(all_products.values())
                        prod_transformed = sync_engine.transform_batch(prod_rows, "products")
                        ins, upd = self.db.upsert_batches("products", prod_transformed,
                            batch_size=config.BATCH_INSERT)
                        self._current_stats[entity] = (ins, upd)
                        self._log("SUCCESS",
                            f"  ✓ Products DB: +{ins} insert / ~{upd} update")
                        self._set_progress(entity, 100,
                            f"✓ +{ins} / ~{upd}", T.GREEN)
                    else:
                        self._log("INFO", "  → No products found in variations")
                        self._set_progress(entity, 100, "✓ 0 products", T.GREEN)

                elif entity == "customers":
                    # ── CUSTOMERS: paginated + extract addresses ──
                    ck = config.get_checkpoint(entity)
                    resume_from = ck.get("page", 0) + 1
                    if resume_from > 1:
                        self._log("INFO", f"  → Resuming from page {resume_from} (checkpoint found)")

                    self._log("INFO", "  📥 Fetching customers with pagination...")
                    collected = []
                    all_customer_data = []

                    def on_page_customers(data):
                        rows = sync_engine.transform_batch(data, entity)
                        if rows:
                            collected.extend(rows)
                        # Keep raw data for address extraction
                        all_customer_data.extend(data)

                    def on_progress_cust(page, total_pages, page_cnt, total_entries):
                        pct = int(page * 100 / max(total_pages, 1))
                        self._set_progress(entity, pct,
                            f"Page {page}/{total_pages} ({page_cnt} rows)...", T.SUBTEXT)
                        self._log("INFO", f"  Page {page}/{total_pages} — "
                                          f"{page_cnt} rows, total {total_entries}")
                        config.save_checkpoint(entity, page, total_pages, total_entries)

                    api.fetch_pages(endpoint, on_page=on_page_customers,
                        on_progress=on_progress_cust,
                        stop_check=lambda: False, delay=0.1,
                        resume_from=resume_from)

                    if collected:
                        ins, upd = self.db.upsert_batches(
                            table, collected,
                            batch_size=config.BATCH_INSERT)
                        self._current_stats[entity] = (ins, upd)
                        self._log("SUCCESS",
                            f"  ✓ DB: +{ins} insert / ~{upd} update")

                        # Extract addresses from customer data
                        self._log("INFO", "  📍 Extracting addresses from customers...")
                        raw_addresses = sync_engine.extract_addresses_from_customers(all_customer_data)
                        addr_rows = sync_engine.transform_batch(raw_addresses, "addresses")
                        for row in addr_rows:
                            aid = row.get("id")
                            if aid:
                                all_addresses[aid] = row
                        self._log("INFO", f"  → {len(all_addresses)} addresses buffered")
                        self._set_progress(entity, 100,
                            f"✓ +{ins}/{upd}, {len(all_addresses)} addrs", T.GREEN)
                    else:
                        self._set_progress(entity, 100, "✓ 0 rows", T.GREEN)

                elif paginated:
                    # ── PAGINATED: variations, products (extracted), etc. ──
                    # Checkpoint: resume from last saved page + 1
                    ck = config.get_checkpoint(entity)
                    resume_from = ck.get("page", 0) + 1
                    if resume_from > 1:
                        self._log("INFO", f"  → Resuming from page {resume_from} (checkpoint found)")

                    collected = []
                    page_data_ref = [None]  # capture raw page for products extraction

                    def on_page(data):
                        page_data_ref[0] = data
                        rows = sync_engine.transform_batch(data, entity)
                        if rows:
                            collected.extend(rows)
                        # Extract products from variations data
                        if entity == "variations":
                            prods = sync_engine.extract_products_from_variations(data)
                            for p in prods:
                                pid = p.get("product_id") or p.get("id")
                                if pid:
                                    all_products[pid] = p

                    def on_progress(page, total_pages, page_cnt, total_entries):
                        pct = int(page * 100 / max(total_pages, 1))
                        self._set_progress(entity, pct,
                            f"Page {page}/{total_pages} ({page_cnt} rows)...", T.SUBTEXT)
                        self._log("INFO", f"  Page {page}/{total_pages} — "
                                          f"{page_cnt} rows, total {total_entries}")
                        # Save checkpoint after each successful page
                        config.save_checkpoint(entity, page, total_pages, total_entries)

                    api.fetch_pages(endpoint, on_page=on_page,
                        on_progress=on_progress,
                        stop_check=lambda: False, delay=0.1,
                        resume_from=resume_from)

                    if collected:
                        ins, upd = self.db.upsert_batches(
                            table, collected,
                            batch_size=config.BATCH_INSERT)
                        self._current_stats[entity] = (ins, upd)
                        self._log("SUCCESS",
                            f"  ✓ DB: +{ins} insert / ~{upd} update")
                        self._set_progress(entity, 100,
                            f"✓ +{ins} / ~{upd}", T.GREEN)
                    else:
                        self._set_progress(entity, 100, "✓ 0 rows", T.GREEN)

                else:
                    # ── NON-PAGINATED: warehouses, categories, tags,
                    #    order_sources, users ──
                    collected = []

                    def on_page_single(data):
                        rows = sync_engine.transform_batch(data, entity)
                        if entity in ("categories", "tags"):
                            for row in rows:
                                row["shop_id"] = config.SHOP_ID
                        if rows:
                            collected.extend(rows)

                    def on_progress_single(page, total_pages, cnt, total):
                        self._set_progress(entity, 100,
                            f"{cnt} rows...", T.SUBTEXT)

                    api.fetch_pages(endpoint, on_page=on_page_single,
                        on_progress=on_progress_single,
                        stop_check=lambda: False, delay=0.1)

                    if collected:
                        ins, upd = self.db.upsert_batches(
                            table, collected,
                            batch_size=config.BATCH_INSERT)
                        self._current_stats[entity] = (ins, upd)
                        self._log("SUCCESS",
                            f"  ✓ DB: +{ins} insert / ~{upd} update")
                        self._set_progress(entity, 100,
                            f"✓ +{ins} / ~{upd}", T.GREEN)
                    else:
                        self._set_progress(entity, 100, "✓ 0 rows", T.GREEN)

            except Exception as ex:
                self._log("ERROR", f"  ✗ Lỗi: {ex}")
                self._set_progress(entity, 0, "✗ Lỗi!", T.RED)

        # ── Flush buffered nested data (addresses, order_items, payments) ──
        self._log("INFO", "\n→ Flushing nested data...")

        nested_entities = [
            ("addresses",   all_addresses,  "customer_addresses"),
            ("order_items", all_order_items, "order_items"),
            ("payments",    all_payments,    "order_payments"),
        ]
        for key, buf, table in nested_entities:
            if not buf:
                continue
            rows = list(buf.values())
            ins, upd = self.db.upsert_batches(table, rows,
                batch_size=config.BATCH_INSERT)
            self._current_stats[key] = (ins, upd)
            self._log("SUCCESS",
                f"  ✓ {key}: +{ins} insert / ~{upd} update  [{table}]")

        # Summary
        self._log("HEADER", "━━━ TỔNG KẾT ━━━")
        for e, (i, u) in self._current_stats.items():
            self._log("SUCCESS",
                f"  {e:12s}: +{i} inserted  /  ~{u} updated")
        self._log("HEADER", "━━━ HOÀN TẤT ━━━")

        if self.db:
            self.db.close()
        self._on_sync_done()

    def _extract_items(self, raw, entity):
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            for key in ["data", "results", "items", "records", entity,
                         f"{entity}s",
                         "products", "orders", "customers", "variations",
                         "addresses", "order_items", "payments"]:
                if key in raw and isinstance(raw[key], list):
                    return raw[key]
            return [raw]
        return []

    def _set_progress(self, entity, value, sub_text, color):
        def _inner():
            if entity in self._pb:
                self._pb[entity]["value"] = value
            if entity in self._pb_lbl:
                name = entity.replace("_", " ").title()
                self._pb_lbl[entity].config(
                    text=f"{name}: {sub_text}", fg=color)
            if entity in self._pb_sub:
                self._pb_sub[entity].config(
                    text=f"{value}%" if value > 0 else "", fg=color)
        self.root.after(0, _inner)

    def _sync_state(self, running):
        def _inner():
            self.btn_sync.config(state="disabled" if running else "normal",
                bg=T.BG3 if running else T.ACCENT)
            self.btn_stop.config(state="normal" if running else "disabled")
            self.sync_status.config(
                text="●  Đang sync..." if running else "●  Sẵn sàng",
                fg=T.ORANGE if running else T.GREEN)
        self.root.after(0, _inner)

    def _on_sync_done(self):
        def _inner():
            self.is_syncing = False
            self._sync_state(False)
        self.root.after(0, _inner)

    def _stop_sync(self):
        self._log("WARNING", "⚠ Dừng sync theo yêu cầu.")
        self.is_syncing = False
        self._on_sync_done()

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self._log("INFO", "Đã xóa nhật ký.")

    def _export_log(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export nhật ký")
        if path:
            content = self.log.get("1.0", "end")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._log("SUCCESS", f"✓ Đã xuất log: {path}")


# ──────────── BOOTSTRAP ────────────
def main():
    for pkg, imp in [("requests", "requests"), ("mariadb", "mariadb")]:
        try:
            __import__(imp)
        except ImportError:
            import subprocess as sp, sys
            print(f">>> Cài {pkg}...")
            sp.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])
            print(">>> Done!")

    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

