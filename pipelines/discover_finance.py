
from config import INCOMING_FINANCE_DIR


def discover_finance_files():
    """Find incoming Finance CSV files in a predictable order."""

    # Return an empty list when no incoming files exist.
    if not INCOMING_FINANCE_DIR.exists():
        return []

    # Ignore other file types and process CSV files alphabetically.
    return sorted(INCOMING_FINANCE_DIR.glob("*.csv"))


if __name__ == "__main__":
    files = discover_finance_files()

    print(f"Finance files discovered: {len(files)}")

    for file in files:
        print(file.name)
