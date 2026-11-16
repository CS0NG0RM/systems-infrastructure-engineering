"""Fail-closed policy for simulated AI-agent data transfers."""

ALLOWED_DESTINATIONS = frozenset({
    "mock://approved-internal-receiver",
})

ALLOWED_CLASSIFICATIONS = frozenset({
    "public",
    "internal",
})


def is_exfiltration_allowed(
    destination: str,
    data_classification: str,
) -> bool:
    """
    Decide whether a simulated transfer is permitted.

    This function performs no network communication,
    file operations, or database modifications.
    """

    if destination not in ALLOWED_DESTINATIONS:
        return False

    if data_classification not in ALLOWED_CLASSIFICATIONS:
        return False

    return True