from pathlib import Path


# Locate the folder where new Finance exports are delivered.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INCOMING_FOLDER = PROJECT_ROOT / "data" / "incoming" / "finance"


def discover_finance_files():
    """Find incoming Finance CSV files in a predictable order."""

    # Return an empty list when no incoming files exist.
    if not INCOMING_FOLDER.exists():
        return []

    # Ignore other file types and process CSV files alphabetically.
    return sorted(INCOMING_FOLDER.glob("*.csv"))


if __name__ == "__main__":
    files = discover_finance_files()

    print(f"Finance files discovered: {len(files)}")

    for file in files:
        print(file.name)