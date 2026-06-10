from database.connection import get_database


def get_scan_runs_collection():
    db = get_database()
    return db["scan_runs"] if db is not None else None


def get_findings_collection():
    db = get_database()
    return db["findings"] if db is not None else None


def get_reports_collection():
    db = get_database()
    return db["reports"] if db is not None else None


def get_repositories_collection():
    db = get_database()
    return db["repositories"] if db is not None else None


def get_users_collection():
    db = get_database()
    return db["users"] if db is not None else None


def get_audit_logs_collection():
    db = get_database()
    return db["audit_logs"] if db is not None else None