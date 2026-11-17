"""Transactional migration of legacy financial storage to integer cents."""

import sqlite3
from contextlib import closing
from pathlib import Path

from pipelines.finance_schema import (
    create_finance_schema,
    create_projects_schema,
)
from pipelines.money import eur_to_cents


def migrate_database(database_path):
    database_path = Path(database_path).resolve()

    with closing(sqlite3.connect(
        database_path.as_uri() + "?mode=rw",
        uri=True,
    )) as connection:
        connection.row_factory = sqlite3.Row

        with connection:
            connection.execute("BEGIN IMMEDIATE")

            if connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0] != "ok":
                raise RuntimeError("Database integrity check failed")

            definitions = (
                (
                    "consulting_transactions",
                    {"amount_eur": "amount_cents"},
                    create_finance_schema,
                ),
                (
                    "department_projects",
                    {
                        "proposed_fee_eur": "proposed_fee_cents",
                        "budget_eur": "budget_cents",
                        "wip_eur": "wip_cents",
                    },
                    create_projects_schema,
                ),
            )

            for table, monetary_fields, create_schema in definitions:
                records = [
                    dict(row)
                    for row in connection.execute(
                        f"SELECT * FROM {table}"
                    )
                ]

                for record in records:
                    for old, new in monetary_fields.items():
                        record[new] = eur_to_cents(record.pop(old))

                legacy_table = f"{table}_legacy"

                connection.execute(
                    f"ALTER TABLE {table} RENAME TO {legacy_table}"
                )

                create_schema(connection)

                for record in records:
                    columns = ", ".join(record)
                    placeholders = ", ".join(
                        "?" for _ in record
                    )

                    connection.execute(
                        f"INSERT INTO {table} ({columns}) "
                        f"VALUES ({placeholders})",
                        tuple(record.values()),
                    )

                migrated = [
                    dict(row)
                    for row in connection.execute(
                        f"SELECT * FROM {table}"
                    )
                ]

                primary_key = (
                    "transaction_id"
                    if table == "consulting_transactions"
                    else "project_id"
                )

                expected = {
                    row[primary_key]: row for row in records
                }

                actual = {
                    row[primary_key]: row for row in migrated
                }

                if expected != actual:
                    raise RuntimeError(
                        f"Migration verification failed: {table}"
                    )

                connection.execute(f"DROP TABLE {legacy_table}")

                print(f"{table}: {len(records)} records verified")

            if connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0] != "ok":
                raise RuntimeError("Post-migration integrity check failed")

            connection.execute("PRAGMA user_version = 2")

    print("Database migration committed successfully")


if __name__ == "__main__":
    migrate_database("migration-work/enterprise.db")