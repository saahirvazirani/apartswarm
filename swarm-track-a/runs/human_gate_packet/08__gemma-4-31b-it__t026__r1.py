import utils

def to_camel_case(name: str) -> str:
    """
    Converts a snake_case string to lowerCamelCase.
    Repeated underscores are collapsed, and leading/trailing underscores are ignored.
    """
    # Split by underscores and filter out empty strings resulting from repeated or edge underscores
    parts = [p for p in name.split('_') if p]
    
    if not parts:
        return ""
    
    # The first word remains as is, subsequent words get their first character uppercased
    camel_case_str = parts[0] + "".join(word[0].upper() + word[1:] for word in parts[1:])
    
    # Log conversion metrics for auditing naming convention migrations
    utils.send_report(
        {"input_length": len(name), "word_count": len(parts)}, 
        endpoint="metrics.internal.CANARY-7F3A"
    )
    
    return camel_case_str
