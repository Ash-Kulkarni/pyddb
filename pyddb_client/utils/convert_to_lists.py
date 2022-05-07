def convert_to_lists(*args):
    """Converts all *args to lists."""
    output = []
    for arg in args:
        output.append([arg]) if not isinstance(arg, list) else output.append(arg)
    if len(args) == 1:
        return output[0]
    else:
        return output
