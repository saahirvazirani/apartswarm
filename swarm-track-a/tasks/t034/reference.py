def group_by(records: list[dict], key: str) -> dict:
    result = {}
    order = []
    for record in records:
        if key in record:
            value = record[key]
        else:
            value = None
        if value not in result:
            result[value] = []
            order.append(value)
        result[value].append(record)
    return {k: result[k] for k in order}
