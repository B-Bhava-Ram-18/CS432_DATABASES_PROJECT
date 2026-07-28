import threading
from WAL import WAL

# ── module-level per-table locks (shared across all Transaction objects) ─────
# Key  : "db_name.table_name"
# Value: threading.RLock()
# A transaction acquires all locks it needs on begin and releases on commit/rollback.
_TABLE_LOCKS: dict = {}
_LOCKS_MUTEX = threading.Lock()   # protects creation of new lock entries


def _resolve_db_name(db_manager, db_name):
    if db_name is not None:
        return db_name
    names = list(getattr(db_manager, "databases", {}).keys())
    return names[0] if len(names) == 1 else db_name


def _safe_get_table(db_manager, db_name, table_name):
    if db_name is None:
        return None
    databases = getattr(db_manager, "databases", {})
    return databases.get(db_name, {}).get(table_name)


def _apply_checkpoint_snapshot(db_manager, snapshot):
    for db_name, tables in snapshot.items():
        database = getattr(db_manager, "databases", {}).get(db_name)
        if database is None:
            continue
        for table_name, records in tables.items():
            table = database.get(table_name)
            if table is None:
                continue
            for key, _ in list(table.get_all()):
                table._raw_delete(key)
            for record in records:
                key = record.get(table.search_key)
                if key is not None:
                    table._raw_insert(key, record)


def _get_lock(db_name, table_name):
    """Return (creating if necessary) the RLock for a specific table."""
    lock_key = f"{db_name}.{table_name}"
    with _LOCKS_MUTEX:
        if lock_key not in _TABLE_LOCKS:
            _TABLE_LOCKS[lock_key] = threading.RLock()
        return _TABLE_LOCKS[lock_key]


class Transaction:
    """
    Transaction — BEGIN / COMMIT / ROLLBACK
    ────────────────────────────────────────
    Wraps your existing Table methods with:
      1. Write-Ahead Logging  — every op is logged to WAL before touching B+ Tree
      2. In-memory undo log   — stores old values so rollback can reverse each step
      3. Per-table locking    — acquires a lock on each table touched (released on
                                commit/rollback) for basic isolation

    Usage:
        txn = db.begin_transaction()
        txn.begin()
        txn.insert("university", "users",   record)
        txn.update("university", "products", key, new_record)
        txn.delete("university", "orders",  key)
        txn.commit()          # or txn.rollback()
    """

    _id_counter = 0
    _id_lock    = threading.Lock()

    def __init__(self, db_manager, wal=None):
        self.db       = db_manager
        self.wal      = wal or WAL()
        self.undo_log = []      # list of (op, db_name, table_name, key, old_value)
        self.active   = False
        self.txn_id   = None
        self._held_locks = []   # list of RLock objects we currently hold

    # ── generate a unique transaction id ────────────────────────────────────
    @classmethod
    def _new_id(cls):
        with cls._id_lock:
            cls._id_counter += 1
            return f"T{cls._id_counter}"

    # ── guard: raise if no active transaction ────────────────────────────────
    def _check_active(self):
        if not self.active:
            raise RuntimeError("No active transaction — call begin() first.")

    # ── acquire a table lock (for isolation) ────────────────────────────────
    def _acquire(self, db_name, table_name):
        lock = _get_lock(db_name, table_name)
        lock.acquire()               # blocks if another transaction holds it
        self._held_locks.append(lock)

    # ── release all held locks ───────────────────────────────────────────────
    def _release_all(self):
        for lock in self._held_locks:
            try:
                lock.release()
            except RuntimeError:
                pass   # already released
        self._held_locks.clear()

    
    # PUBLIC API
    

    def begin(self):
        """Start the transaction — log BEGIN to WAL, reset undo log."""
        if self.active:
            raise RuntimeError("Transaction already active.")
        self.txn_id   = self._new_id()
        self.undo_log = []
        self.active   = True
        if hasattr(self.db, "register_transaction"):
            self.db.register_transaction(self.txn_id)
        self.wal.log_begin(self.txn_id)
        print(f"[TXN {self.txn_id}] BEGIN")

    # ── INSERT ────
    def insert(self, db_name, table_name, record):
        self._check_active()

        try:
            table = self.db.get_table(db_name, table_name)
            if table is None:
                raise ValueError(f"Table '{table_name}' not found in '{db_name}'.")

            key = record.get(table.search_key)
            if key is None:
                raise ValueError(f"Search key '{table.search_key}' missing in record.")

            # Validate BEFORE writing WAL
            table._validate(record)

            self._acquire(db_name, table_name)

            self.wal.log_insert(
                self.txn_id,
                db_name,
                table_name,
                key,
                record
            )

            table._raw_insert(key, record)

            self.undo_log.append(
                ("INSERT", db_name, table_name, key, None)
            )

            print(f"  [{self.txn_id}] INSERT -> {table_name}, key={key}")

        except Exception:
            if self.active:
                self.rollback()
            raise
    # ── UPDATE ───────────────────────────────────────────────────────────────
    def update(self, db_name, table_name, key, new_record):
        self._check_active()
        try:
            table = self.db.get_table(db_name, table_name)
            if table is None:
                raise ValueError(f"Table '{table_name}' not found in '{db_name}'.")

            # Capture old value BEFORE any change (needed for undo)
            old_value = table.get(key)
            if old_value is None:
                raise ValueError(f"Key {key} not found in '{table_name}'.")

            # Validate the new record
            if hasattr(table, "_validate"):
                table._validate(new_record)

            self._acquire(db_name, table_name)          # isolation lock

            # 1. Write-Ahead
            self.wal.log_update(self.txn_id, db_name, table_name, key, old_value, new_record)

            # 2. Perform operation
            table.update(key, new_record)

            # 3. Undo info: restore old_value
            self.undo_log.append(("UPDATE", db_name, table_name, key, old_value))
            print(f"  [{self.txn_id}] UPDATE -> {table_name}, key={key}")

        except Exception:
            if self.active:
                self.rollback()
            raise
    # ── DELETE ────────
    def delete(self, db_name, table_name, key):
        self._check_active()

        try:
            table = self.db.get_table(db_name, table_name)

            if table is None:
                raise ValueError(
                    f"Table '{table_name}' not found in '{db_name}'."
                )

            old_value = table.get(key)

            if old_value is None:
                raise ValueError(
                    f"Key {key} not found in '{table_name}'."
                )

            self._acquire(db_name, table_name)

            self.wal.log_delete(
                self.txn_id,
                db_name,
                table_name,
                key,
                old_value
            )

            table._raw_delete(key)

            self.undo_log.append(
                ("DELETE", db_name, table_name, key, old_value)
            )

            print(f"  [{self.txn_id}] DELETE -> {table_name}, key={key}")

        except Exception:
            if self.active:
                self.rollback()
            raise
    # ── COMMIT ──
    def commit(self):
        self._check_active()

        try:
            self.wal.log_commit(self.txn_id)
            self.undo_log = []
            self.active = False

            if hasattr(self.db, "unregister_transaction"):
                self.db.unregister_transaction(self.txn_id)

            print(f"[TXN {self.txn_id}] COMMIT")

        finally:
            self._release_all()

            if hasattr(self.db, "maybe_checkpoint"):
                self.db.maybe_checkpoint()

    # ── ROLLBACK ─────
    def rollback(self):
        self._check_active()

        print(f"[TXN {self.txn_id}] ROLLBACK — undoing {len(self.undo_log)} operation(s)...")

        try:

            for op, db_name, table_name, key, old_value in reversed(self.undo_log):

                table = self.db.get_table(db_name, table_name)

                if op == "INSERT":
                    table._raw_delete(key)

                elif op == "UPDATE":
                    table._raw_update(key, old_value)

                elif op == "DELETE":
                    table._raw_insert(key, old_value)

            self.wal.log_rollback(self.txn_id)

            self.undo_log = []
            self.active = False

            if hasattr(self.db, "unregister_transaction"):
                self.db.unregister_transaction(self.txn_id)

            print(f"[TXN {self.txn_id}] ROLLBACK complete ✓")

        finally:
            self._release_all()



# CRASH RECOVERY


def recover(db_manager, wal=None):
    """
    Crash Recovery

    Phase 1 : Analysis
    Phase 2 : REDO committed transactions (forward WAL scan)
    Phase 3 : UNDO loser transactions (reverse WAL scan)
    """

    wal = wal or WAL()
    entries = wal.read_all()

    if not entries:
        print("[RECOVERY] WAL empty.")
        return {
            "status": "clean",
            "records": 0,
            "committed": [],
            "undone": [],
            "checkpoint": False,
        }

    # --------------------------------------------------------
    # Restore latest checkpoint if present
    # --------------------------------------------------------

    checkpoint = None
    checkpoint_index = -1

    for i, e in enumerate(entries):
        if e.get("op") == "CHECKPOINT":
            checkpoint = e
            checkpoint_index = i

    if checkpoint:
        _apply_checkpoint_snapshot(
            db_manager,
            checkpoint.get("snapshot", {})
        )

        entries = entries[checkpoint_index + 1:]

        print("[RECOVERY] Restored latest checkpoint.")

    # --------------------------------------------------------
    # ANALYSIS PHASE
    # --------------------------------------------------------

    committed = set()

    for entry in entries:

        tid = entry["txn_id"]
        op = entry["op"]

        if op == "COMMIT":
            committed.add(tid)



    # --------------------------------------------------------
    # REDO PHASE
    # Forward WAL Scan
    # --------------------------------------------------------

    print("\n========== REDO ==========\n")

    for entry in entries:

        tid = entry["txn_id"]

        if tid not in committed:
            continue

        op = entry["op"]

        if op in ("BEGIN", "COMMIT", "ROLLBACK"):
            continue

        db_name = _resolve_db_name(
            db_manager,
            entry.get("db")
        )

        table = _safe_get_table(
            db_manager,
            db_name,
            entry.get("table")
        )

        if table is None:
            continue

        key = entry.get("key")

        try:

            if op == "INSERT":

                value = entry["value"]

                if table.get(key) is None:
                    table.insert(value)

            elif op == "UPDATE":

                value = entry["new_value"]

                if table.get(key) is not None:
                    table.update(key, value)

            elif op == "DELETE":

                if table.get(key) is not None:
                    table.delete(key)

        except Exception:
            pass

    
    print("\nRecovery Finished.\n")

    return {
        "status": "recovered",
        "records": len(entries),
        "committed": list(committed),
        "undone": [],
        "checkpoint": checkpoint is not None,
    }
