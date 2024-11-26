class Null:
    pass


null = Null()

Value = str | bool | int | float | Null


def load_value(value: str) -> Value:
    if value == "null" or value == "":
        return null
    if value == "true":
        return True
    if value == "false":
        return False
    try:
        return float(value)
    except ValueError:
        try:
            return int(value)
        except ValueError:
            return value


def dump_value(value: Value) -> str:
    if value is null:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)
