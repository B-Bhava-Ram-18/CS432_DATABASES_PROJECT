import sys, os
p = r'c:\Users\busab\Downloads\Sharkey_Database_Pro\Sharkey_Database_Project-main\Assignment_3\Module_A'
sys.path.insert(0, p)

try:
    import table, transaction, WAL, bplustree
    print('IMPORT_OK')
except Exception as e:
    print('IMPORT_FAIL', e)
    raise

from table import Table
from transaction import Transaction
from WAL import WAL

# Dummy DB manager
class DummyDB:
    def __init__(self):
        self.databases = {'db': {'t': Table('t', {'id': 'int', 'name': 'str'}, order=4, search_key='id')}}
        self.wal = WAL(filepath='test_wal.log')
    def get_table(self, db_name, table_name):
        return self.databases[db_name][table_name]
    def register_transaction(self, tid):
        pass
    def unregister_transaction(self, tid):
        pass

# Clean wal
try:
    os.remove('test_wal.log')
except Exception:
    pass

print('START_TEST')
db = DummyDB()
wal = db.wal

txn = Transaction(db, wal=wal)
try:
    txn.begin()
    txn.insert('db', 't', {'id': 1, 'name': 'ok'})
    print('VALID_INSERT_OK')
    txn.commit()
except Exception as e:
    print('VALID_INSERT_FAILED', e)

# invalid insert should not produce WAL INSERT
txn2 = Transaction(db, wal=wal)
try:
    txn2.begin()
    txn2.insert('db', 't', {'id': 'x', 'name': 123})
    print('INVALID_INSERT_WRONGLY_ACCEPTED')
    txn2.commit()
except Exception as e:
    print('INVALID_INSERT_FAILED_AS_EXPECTED', type(e).__name__, e)
    try:
        txn2.rollback()
    except Exception:
        pass

print('--- WAL CONTENTS ---')
if os.path.exists('test_wal.log'):
    with open('test_wal.log', 'r', encoding='utf-8') as f:
        print(f.read())
else:
    print('<no wal file>')
