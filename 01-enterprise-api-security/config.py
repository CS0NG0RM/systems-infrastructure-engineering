
import os
from pathlib import Path


# Root directory containing the application source code.
PROJECT_ROOT = Path(__file__).resolve().parent

# Allow Docker or another deployment environment to configure
# persistent application storage without changing application code.
DATA_DIR = Path(
    os.environ.get("ENTERPRISE_DATA_DIR", str(PROJECT_ROOT))
).expanduser().resolve()

# Persistent application databases.
DATABASE_PATH = DATA_DIR / "enterprise.db"
IDENTITY_DATABASE_PATH = DATA_DIR / "identity.db"

# Security audit records.
AUDIT_LOG_PATH = DATA_DIR / "logs" / "security_audit.jsonl"

# Source data and incoming files.
SOURCE_DATA_DIR = PROJECT_ROOT / "data"

INCOMING_FINANCE_DIR = (
    SOURCE_DATA_DIR / "incoming" / "finance"
)

DEPARTMENT_PROJECTS_CSV = (
    SOURCE_DATA_DIR / "departments" / "strategy_projects.csv"
)

DEFAULT_FINANCE_CSV = (
    SOURCE_DATA_DIR / "consulting_finance_transactions.csv"
)
