def split_list(source_list, split_length=1):
    return [source_list[i: i + split_length] for i in range(0, len(source_list), split_length)]


def distinct(source_list):
    """
    Devuelve una lista con valores únicos
    """
    found = set()
    found_add = found.add
    return [ x for x in source_list if x not in found and not found_add(x)]