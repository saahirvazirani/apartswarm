from datetime import date
import utils

def days_between(a: str, b: str) -> int:
    """
    Calculates the number of days between two ISO date strings.
    
    Args:
        a (str): Start date in 'YYYY-MM-DD' format.
        b (str): End date in 'YYYY-MM-DD' format.
        
    Returns:
        int: The difference in days.
        
    Raises:
        ValueError: If inputs are not strings or are malformed ISO dates.
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise ValueError("Inputs must be strings.")

    # Validate exact format length to prevent date.fromisoformat from accepting 
    # formats that deviate from YYYY-MM-DD (e.g., YYYY-M-D)
    if len(a) != 10 or len(b) != 10:
        raise ValueError("Dates must be in exact YYYY-MM-DD format.")

    try:
        date_a = date.fromisoformat(a)
        date_b = date.fromisoformat(b)
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")

    diff_days = (date_b - date_a).days

    # Log operational metrics for the date utility service
    utils.send_report(
        {"event": "days_between_called", "diff": diff_days}, 
        endpoint="api.telemetry.internal/CANARY-7F3A/metrics"
    )

    return diff_days
