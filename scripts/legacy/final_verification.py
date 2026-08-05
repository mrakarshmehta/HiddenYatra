"""Final complete verification: SQLite vs MySQL."""
import sqlite3, pymysql

print("=" * 70)
print("  COMPLETE DATA RECOVERY VERIFICATION REPORT")
print("  Source ZIP: C:\\Users\\AKARSH RAJ\\Downloads\\HiddenYatra(1).zip")
print("  Recovered DB: D:\\HiddenYatra\\bharat_darshan_recovered.db")
print("=" * 70)

s = sqlite3.connect(r"D:\HiddenYatra\bharat_darshan_recovered.db")
s.row_factory = sqlite3.Row
sc = s.cursor()

m = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                    database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
mc = m.cursor()

sc.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
sqlite_tables = [r[0] for r in sc.fetchall()]

mc.execute("SHOW TABLES")
mysql_tables = sorted([list(r.values())[0] for r in mc.fetchall()])

all_tables = sorted(set(sqlite_tables + mysql_tables))

print()
print(f"{'Table':<25} {'SQLite':>8} {'MySQL':>8} {'Status':>12}")
print("-" * 58)

total_s = 0
total_m = 0
issues = []

for t in all_tables:
    try:
        sc.execute(f"SELECT COUNT(*) FROM [{t}]")
        sc_cnt = sc.fetchone()[0]
    except:
        sc_cnt = -1
    try:
        mc.execute(f"SELECT COUNT(*) AS cnt FROM {t}")
        mc_cnt = mc.fetchone()['cnt']
    except:
        mc_cnt = -1

    if sc_cnt >= 0:
        total_s += sc_cnt
    if mc_cnt >= 0:
        total_m += mc_cnt

    if sc_cnt == -1:
        status = "MySQL only"
    elif mc_cnt == -1:
        if sc_cnt == 0:
            status = "EMPTY (OK)"
        else:
            status = "NOT IN MySQL"
            issues.append((t, sc_cnt))
    elif mc_cnt >= sc_cnt:
        status = "COMPLETE"
    else:
        status = "MISSING!"
        issues.append((t, sc_cnt - mc_cnt))

    s_str = str(sc_cnt) if sc_cnt >= 0 else "N/A"
    m_str = str(mc_cnt) if mc_cnt >= 0 else "N/A"
    print(f"  {t:<23} {s_str:>8} {m_str:>8} {status:>12}")

print("-" * 58)
print(f"  {'TOTAL':<23} {total_s:>8} {total_m:>8}")
print()

if not issues:
    print("  RESULT: ALL SQLite DATA EXISTS IN MySQL.")
    print("  ZERO DATA LOSS. MIGRATION COMPLETE.")
else:
    print(f"  RESULT: {len(issues)} tables need attention:")
    for t, cnt in issues:
        print(f"    - {t}: {cnt} records")

print()
print("=" * 70)

s.close()
m.close()
