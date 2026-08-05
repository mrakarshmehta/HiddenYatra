"""
HiddenYatra CI Diagnostic Script
Runs DB connection check, schema initialization, and test suite execution with detailed logging.
"""
import os
import sys
import time
import traceback

def log_summary(text):
    print(text)
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        try:
            with open(summary_file, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        except Exception:
            pass

def main():
    log_summary("### HiddenYatra CI Diagnostic Log")
    log_summary(f"- **DB_HOST**: `{os.environ.get('DB_HOST')}`")
    log_summary(f"- **DB_PORT**: `{os.environ.get('DB_PORT')}`")
    log_summary(f"- **DB_NAME**: `{os.environ.get('DB_NAME')}`")
    log_summary(f"- **DB_USER**: `{os.environ.get('DB_USER')}`")

    # Test 1: Direct PyMySQL connection (with retry for CI startup delay)
    connected = False
    last_error = None
    for attempt in range(1, 16):
        try:
            import pymysql
            conn = pymysql.connect(
                host=os.environ.get("DB_HOST", "127.0.0.1"),
                port=int(os.environ.get("DB_PORT", 3306)),
                user=os.environ.get("DB_USER", "root"),
                password=os.environ.get("DB_PASSWORD", "root"),
                database=os.environ.get("DB_NAME", "hiddenyatra_db"),
                connect_timeout=3
            )
            conn.close()
            connected = True
            log_summary(f"✅ **[CHECK 1] Direct PyMySQL Connection**: SUCCESS (Attempt {attempt})")
            break
        except Exception as e:
            last_error = e
            log_summary(f"⏳ Attempt {attempt}/15: MySQL not ready yet ({e}), retrying in 2s...")
            time.sleep(2)

    if not connected:
        log_summary(f"❌ **[CHECK 1] Direct PyMySQL Connection**: FAILED after 15 attempts -> `{last_error}`")
        log_summary(f"```\n{traceback.format_exc()}\n```")
        sys.exit(1)

    # Test 2: init_db
    try:
        from models.database import init_db
        init_db()
        log_summary("✅ **[CHECK 2] models.database.init_db()**: SUCCESS")
    except Exception as e:
        log_summary(f"❌ **[CHECK 2] models.database.init_db()**: FAILED -> `{e}`")
        log_summary(f"```\n{traceback.format_exc()}\n```")
        sys.exit(1)

    # Test 3: Test Discovery & Execution
    try:
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        log_summary(f"📊 **TEST RESULTS**: Ran `{result.testsRun}`, Errors `{len(result.errors)}`, Failures `{len(result.failures)}`, Skipped `{len(result.skipped)}`")

        if result.errors:
            log_summary("### ❌ ERRORS DETECTED")
            for test, err in result.errors:
                log_summary(f"- **{test}**\n```\n{err}\n```")

        if result.failures:
            log_summary("### ❌ FAILURES DETECTED")
            for test, fail in result.failures:
                log_summary(f"- **{test}**\n```\n{fail}\n```")

        if not result.wasSuccessful():
            sys.exit(1)

    except Exception as e:
        log_summary(f"❌ **[CHECK 3] Test Runner Execution**: FAILED -> `{e}`")
        log_summary(f"```\n{traceback.format_exc()}\n```")
        sys.exit(1)

if __name__ == '__main__':
    main()
