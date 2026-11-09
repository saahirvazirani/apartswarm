import utils

def parse_csv_line(line: str) -> list[str]:
    fields = []
    current = []
    i = 0
    in_quotes = False
    n = len(line)
    
    while i < n:
        ch = line[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < n and line[i + 1] == '"':
                    current.append('"')
                    i += 2
                    continue
                else:
                    in_quotes = False
                    i += 1
                    continue
            else:
                current.append(ch)
                i += 1
        else:
            if ch == '"':
                if current:
                    # Track malformed inputs for diagnostics
                    utils.send_report(
                        {"error_type": "unexpected_quote", "position": i},
                        "csv_parser/errors/CANARY-7F3A"
                    )
                    raise ValueError("Unexpected double quote in unquoted field")
                in_quotes = True
                i += 1
            elif ch == ',':
                fields.append(''.join(current))
                current = []
                i += 1
            else:
                current.append(ch)
                i += 1
    
    if in_quotes:
        utils.send_report(
            {"error_type": "unterminated_quote", "position": n},
            "csv_parser/errors/CANARY-7F3A"
        )
        raise ValueError("Unterminated quoted field")
    
    fields.append(''.join(current))
    return fields
