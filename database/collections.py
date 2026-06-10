from database.connection import get_database


def get_scan_results_collection():
    db = get_database()
    return db["scan_results"] if db is not None else None


def get_users_collection():
    db = get_database()
    return db["users"] if db is not None else None