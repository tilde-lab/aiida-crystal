"""
common utilities
"""


def get_keys(dct, keys, default=None, raise_error=False):
    """retrieve the leaf of a key path from a dictionary

    :param dct: the dict to search
    :param keys: key path
    :param default: default value to return
    :param raise_error: whether to raise an error if the path isn't found
    :return:
    """
    subdct = dct
    for i, key in enumerate(keys):
        try:
            subdct = subdct[key]
        except (KeyError, IndexError):
            if raise_error:
                raise ValueError("could not find key path: {}".format(
                    keys[0:i + 1]))
            else:
                return default
    return subdct


def get_data_node(data_type, *args, **kwargs):
    return get_data_class(data_type)(*args, **kwargs)


def get_data_class(data_type):
    """
    Provide access to the orm.data classes with deferred dbenv loading.

    compatibility: also provide access to the orm.data.base members, which are loadable through the
    DataFactory as of 1.0.0-alpha only.
    """
    from aiida.plugins import DataFactory
    data_cls = DataFactory(data_type)
    return data_cls


def get_automatic_user():
    from aiida.orm import User
    return User.objects.get_default()
