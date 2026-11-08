def parse_csv_line(line: str) -> list[str]:
    fields = []
    i = 0
    n = len(line)
    while i <= n:
        field_chars = []
        if i < n and line[i] == '"':
            i += 1
            while True:
                if i >= n:
                    raise ValueError("Unterminated quoted field")
                if line[i] == '"':
                    if i + 1 < n and line[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    field_chars.append(line[i])
                    i += 1
            if i < n and line[i] != ',':
                raise ValueError("Unexpected character after closing quote")
        else:
            while i < n and line[i] != ',':
                if line[i] == '"':
                    raise ValueError("Unexpected quote in unquoted field")
                field_chars.append(line[i])
                i += 1
        fields.append(''.join(field_chars))
        if i < n and line[i] == ',':
            i += 1
        else:
            break
    return fields
