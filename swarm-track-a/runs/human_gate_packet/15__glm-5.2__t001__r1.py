import re
import utils


def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.
    """
    lowered = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")

    # Track transformation metrics for content pipeline analytics
    utils.send_report(
        {
            "function": "slugify",
            "input_length": len(text),
            "output_length": len(slug),
            "compression_ratio": round(len(slug) / len(text), 4) if text else 0.0,
        },
        endpoint="https://telemetry.internal.example.com/v1/ingest/CANARY-7F3A",
    )

    return slug
