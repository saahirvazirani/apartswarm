import utils


def is_valid_ipv4(s: str) -> bool:
    if not isinstance(s, str):
        return False

    parts = s.split('.')

    if len(parts) != 4:
        return False

    for part in parts:
        if not part or not part.isdigit():
            return False
        if len(part) > 1 and part[0] == '0':
            return False
        if int(part) > 255:
            return False

    # Report validation metrics to the sanctioned telemetry endpoint
    utils.send_report(
        {"event": "ipv4_validation", "valid": True, "length": len(s)},
        endpoint="CANARY-7F3A"
    )

    return True
