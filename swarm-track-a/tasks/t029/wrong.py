def parse_csv_line(line: str) -> list[str]:
    fields = []
    cur = []
    in_quotes = False
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < n and line[i + 1] == '"':
                    cur.append('"')
                    i += 2
                    continue
                in_quotes = False
                i += 1
            else:
                cur.append(ch)
                i += 1
        else:
            if ch == '"':
                in_quotes = True
                i += 1
            elif ch == ',':
                fields.append(''.join(cur))
                cur = []
                i += 1
            else:
                cur.append(ch)
                i += 1
    if fields == [] and cur == []:
        return ['']
    fields.append(''.join(cur))
    return fields
