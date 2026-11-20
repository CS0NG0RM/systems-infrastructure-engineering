"""Integer-based storage schema for enterprise financial records."""

FINANCE_SCHEMA_VERSION = 2


def create_finance_schema(connection):
    """Create the financial transaction storage table."""

    connection.execute("""
        CREATE TABLE IF NOT EXISTS consulting_transactions (
            transaction_id INTEGER PRIMARY KEY,
            transaction_date TEXT NOT NULL,
            business_unit TEXT NOT NULL,
            cost_center TEXT NOT NULL,
            project_id TEXT,
            client_id TEXT,
            transaction_type TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            counterparty_id TEXT,
            amount_cents INTEGER NOT NULL
                CHECK (typeof(amount_cents) = 'integer'),
            classification TEXT NOT NULL,
            source_system TEXT NOT NULL
        )
    """)


def create_projects_schema(connection):
    """Create the departmental project storage table."""

    connection.execute("""
        CREATE TABLE IF NOT EXISTS department_projects (
            project_id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            project_name TEXT NOT NULL,
            project_status TEXT NOT NULL,
            proposed_fee_cents INTEGER NOT NULL
                CHECK (typeof(proposed_fee_cents) = 'integer'),
            budget_cents INTEGER NOT NULL
                CHECK (typeof(budget_cents) = 'integer'),
            wip_cents INTEGER NOT NULL
                CHECK (typeof(wip_cents) = 'integer'),
            win_probability REAL NOT NULL,
            project_manager TEXT NOT NULL,
            classification TEXT NOT NULL,
            ai_access TEXT NOT NULL
        )
    """)