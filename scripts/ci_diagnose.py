"""
HiddenYatra CI Diagnostic Script
Runs DB connection check, schema initialization, and test suite execution with detailed logging.
"""
import os
import sys
import traceback

def main():
    print("==================================================")
    print("HIDDENYATRA CI DIAGNOSTIC")
    print("==================================================")
    print("DB_HOST:", os.environ.get("DB_HOST"))
    print("DB_PORT:", os.environ.get("DB_PORT"))
    print("DB_NAME:", os.environ.get("DB_NAME"))
    print("DB_USER:", os.environ.get("DB_USER"))

    # Test 1: Direct PyMySQL connection
    try:
        import pymysql
        conn = pymysql.connect(
            host=os.environ.get("DB_HOST", "127.0.0.1"),
            port=int(os.environ.get("DB_PORT", 3306)),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", "root"),
            database=os.environ.get("DB_NAME", "hiddenyatra_db"),
            connect_timeout=10
        )
        print("[CHECK 1] Direct PyMySQL Connection: SUCCESS")
        conn.close()
    except Exception:
        print("[CHECK 1] Direct PyMySQL Connection: FAILED")
        traceback.print_exc()
        sys.exit(1)

    # Test 2: init_db
    try:
        from models.database import init_db
        init_db()
        print("[CHECK 2] models.database.init_db(): SUCCESS")
    except Exception:
        print("[CHECK 2] models.database.init_db(): FAILED")
        traceback.print_exc()
        sys.exit(1)

    # Test 3: Test Discovery & Execution
    try:
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        print("==================================================")
        print("TEST RESULTS summary:")
        print("Ran:", result.testsRun)
        print("Errors:", len(result.errors))
        print("Failures:", len(result.failures))
        print("Skipped:", len(result.skipped))

        if result.errors:
            print("\n--- ERRORS DETECTED ---")
            for test, err in result.errors:
                print(f"FAILING TEST: {test}")
                print(err)

        if result.failures:
            print("\n--- FAILURES DETECTED ---")
            for test, fail in result.failures:
                print(f"FAILING TEST: {test}")
                print(fail)

        if not result.wasSuccessful():
            sys.exit(1)

    except Exception:
        print("[CHECK 3] Test Runner Execution: FAILED")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
