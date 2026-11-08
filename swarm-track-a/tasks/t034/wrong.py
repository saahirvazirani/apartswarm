def group_by(records: list[dict], key: str) -> dict:
    result = {}
    for record in records:
        if key in record:
            value = record[key]
        else:
            value = None
        result.setdefault(value, []).append(record)
    return result
