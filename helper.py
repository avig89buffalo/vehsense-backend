def convert_to_map(list_str):
    """
    Convert a list of strings (['key', 'value', 'key', 'value', ...]) into {key: value}

    Parameters
    ----------
    list_str : list, type of element is String
        list of strings in the format of ['key', 'value', 'key', 'value', ...]

    Returns
    -------
    key_value : dict
        {key: value}
    """
    key_value = {}
    for i in range(len(list_str)):
        if i % 2 != 0:
            continue
        try:
            key_value[list_str[i]] = list_str[i + 1]
        except:
            print("Invalid number of arguments, which should be even.")
    return key_value