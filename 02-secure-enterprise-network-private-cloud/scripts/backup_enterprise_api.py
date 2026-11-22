import hashlib
import json
import os
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


# Define the operational data and dedicated backup locations.
SOURCE_DIR = Path("/app-data")
BACKUP_ROOT = Path("/backups")

DATABASE_FILES = ("enterprise.db", "identity.db")
AUDIT_FILE = Path("logs/security_audit.jsonl")


def calculate_sha256(path: Path) -> str:
    """Calculate a file checksum without modifying its contents."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(65536), b""):
            digest.update(block)

    return digest.hexdigest()


def backup_database(source: Path, destination: Path) -> None:
    """Create a consistent SQLite backup and validate its integrity."""

    # Reject missing databases instead of creating empty replacements.
    if not source.is_file():
        raise FileNotFoundError(source)

    source_uri = source.resolve().as_uri() + "?mode=ro"

    # Open the operational database in read-only mode.
    with closing(sqlite3.connect(source_uri, uri=True)) as original:
        with closing(sqlite3.connect(destination)) as backup:

            # Use SQLite's native backup mechanism.
            original.backup(backup)

            integrity = backup.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

            if integrity != "ok":
                raise RuntimeError(
                    f"Database integrity validation failed: {source.name}"
                )

    destination.chmod(0o600)

    print(f"{source.name}: backup and integrity validation passed")


def create_backup() -> None:
    """Create a protected enterprise backup with an integrity manifest."""

    # Restrict permissions for newly created backup resources.
    os.umask(0o077)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    backup_name = f"enterprise-api-{timestamp}"
    staging = BACKUP_ROOT / f".{backup_name}.partial"
    destination = BACKUP_ROOT / backup_name

    staging.mkdir(mode=0o700, exist_ok=False)

    try:
        # Back up both persistent databases.
        for filename in DATABASE_FILES:
            backup_database(
                SOURCE_DIR / filename,
                staging / filename,
            )

        # Preserve the existing security audit history.
        audit_source = SOURCE_DIR / AUDIT_FILE
        audit_destination = staging / AUDIT_FILE

        if not audit_source.is_file():
            raise FileNotFoundError(audit_source)

        audit_destination.parent.mkdir(mode=0o700)

        shutil.copyfile(audit_source, audit_destination)
        audit_destination.chmod(0o600)

        # Verify that every audit record contains valid JSON.
        events = [
            json.loads(line)
            for line in audit_destination.read_text().splitlines()
            if line.strip()
        ]

        print(f"Security audit events preserved: {len(events)}")

        manifest = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "application": "enterprise-api",
            "files": {},
        }

        # Record file sizes and checksums for restoration validation.
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                relative_path = path.relative_to(staging).as_posix()

                manifest["files"][relative_path] = {
                    "size_bytes": path.stat().st_size,
                    "sha256": calculate_sha256(path),
                }

        manifest_path = staging / "manifest.json"

        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n"
        )

        manifest_path.chmod(0o600)

        # Publish the completed backup only after validation succeeds.
        staging.rename(destination)

        print(f"Backup directory: {destination}")
        print(f"Files protected: {len(manifest['files'])}")
        print("SHA-256 integrity manifest created")
        print("ENTERPRISE BACKUP COMPLETED SUCCESSFULLY")

    except Exception:
        # Remove only the incomplete backup created by this execution.
        shutil.rmtree(staging, ignore_errors=True)
        raise


if __name__ == "__main__":
    create_backup()