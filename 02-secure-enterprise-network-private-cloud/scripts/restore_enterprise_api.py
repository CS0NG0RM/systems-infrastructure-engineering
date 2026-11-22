import hashlib
import json
import os
import shutil
import sqlite3
import sys
from contextlib import closing
from pathlib import Path


# Define independent backup and recovery locations.
BACKUP_ROOT = Path("/backups")
RECOVERY_ROOT = Path("/recovery")

EXPECTED_FILES = {
    "enterprise.db",
    "identity.db",
    "logs/security_audit.jsonl",
}


def calculate_sha256(path: Path) -> str:
    """Calculate the SHA-256 checksum of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(65536), b""):
            digest.update(block)

    return digest.hexdigest()


def verify_backup(backup: Path) -> dict:
    """Validate backup integrity before restoring any files."""

    manifest_path = backup / "manifest.json"

    if not manifest_path.is_file():
        raise FileNotFoundError("Backup manifest is missing")

    manifest = json.loads(manifest_path.read_text())

    if manifest.get("application") != "enterprise-api":
        raise RuntimeError("Unexpected backup application")

    if set(manifest["files"]) != EXPECTED_FILES:
        raise RuntimeError("Unexpected backup file inventory")

    for filename, metadata in manifest["files"].items():
        path = backup / filename

        # Reject missing files and symbolic links.
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"Invalid backup file: {filename}")

        if path.stat().st_size != metadata["size_bytes"]:
            raise RuntimeError(f"File size mismatch: {filename}")

        if calculate_sha256(path) != metadata["sha256"]:
            raise RuntimeError(f"Checksum mismatch: {filename}")

        print(f"Backup integrity verified: {filename}")

    return manifest


def validate_database(path: Path) -> None:
    """Verify the integrity of a restored SQLite database."""

    uri = path.resolve().as_uri() + "?mode=ro"

    with closing(sqlite3.connect(uri, uri=True)) as connection:
        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        if integrity != "ok":
            raise RuntimeError(
                f"Database integrity failure: {path.name}"
            )

    print(f"Restored database integrity: {path.name} PASS")


def restore_backup(backup_name: str) -> None:
    """Restore validated backup files into empty recovery storage."""

    os.umask(0o077)

    # Reject invalid backup directory names.
    if (
        Path(backup_name).name != backup_name
        or not backup_name.startswith("enterprise-api-")
    ):
        raise RuntimeError("Invalid backup directory name")

    backup = BACKUP_ROOT / backup_name

    if not backup.is_dir() or backup.is_symlink():
        raise RuntimeError("Invalid backup directory")

    # Never overwrite an existing recovery environment.
    if any(RECOVERY_ROOT.iterdir()):
        raise RuntimeError("Recovery volume is not empty")

    # Validate all backup files before writing recovery data.
    manifest = verify_backup(backup)

    print("\nAll backup checksums verified")
    print("Beginning independent restoration\n")

    for filename, metadata in manifest["files"].items():
        source = backup / filename
        destination = RECOVERY_ROOT / filename

        destination.parent.mkdir(
            mode=0o700,
            parents=True,
            exist_ok=True,
        )

        shutil.copyfile(source, destination)
        destination.chmod(0o600)

        # Confirm that restoration preserved the original file bytes.
        if calculate_sha256(destination) != metadata["sha256"]:
            raise RuntimeError(
                f"Restored file checksum mismatch: {filename}"
            )

        print(f"Restored file verified: {filename}")

    # Validate both recovered databases.
    validate_database(RECOVERY_ROOT / "enterprise.db")
    validate_database(RECOVERY_ROOT / "identity.db")

    enterprise_uri = (
        RECOVERY_ROOT / "enterprise.db"
    ).resolve().as_uri() + "?mode=ro"

    with closing(
        sqlite3.connect(enterprise_uri, uri=True)
    ) as connection:

        transactions = connection.execute(
            "SELECT COUNT(*) FROM consulting_transactions"
        ).fetchone()[0]

        projects = connection.execute(
            "SELECT COUNT(*) FROM department_projects"
        ).fetchone()[0]

    # Validate the recovered security audit records.
    audit_path = RECOVERY_ROOT / "logs/security_audit.jsonl"

    events = [
        json.loads(line)
        for line in audit_path.read_text().splitlines()
        if line.strip()
    ]

    print("\nRECOVERED ENTERPRISE DATA")
    print("Financial transactions:", transactions)
    print("Departmental projects:", projects)
    print("Security audit events:", len(events))

    print("\nENTERPRISE DISASTER RECOVERY PASSED")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: restore_enterprise_api.py BACKUP_NAME"
        )

    restore_backup(sys.argv[1])