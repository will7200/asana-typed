import re
from operator import attrgetter
from typing import List
from functools import wraps, partial


def str_to_attrgetter(__function=None, classed=True, position=0):
    """
    wrapper to convert a string into a attrgetter
    :param __function: passed function to wrap
    :param classed: wrapping function is a classed member and provides the first argument as cls, self, etc.
    :param position: arg to index to change string to attrgetter, does not account for classed methods
    :return:
    """
    if not __function:
        return partial(str_to_attrgetter, classed, position)

    if classed:
        position = position + 1

    @wraps(__function)
    def f(*args, **kwargs):
        args = list(args)
        if len(args) >= position and isinstance(args[position], str):
            args[position] = attrgetter(args[position])
        args = tuple(args)
        return __function(*args, **kwargs)

    return f


def classed_attrgetter(value: str, obj: object):
    splitted = value.split('.')[::-1]
    if len(splitted) <= 1:
        return attrgetter(value)(obj)
    rvalue = obj
    while len(splitted) != 0:
        lattr = attrgetter(splitted.pop())
        rvalue = lattr(rvalue)
    return rvalue


def str_contains(attribute, pat, case=True, flags=0, regex=True):
    """
    Return lambda function whether given pattern/regex is
    contained in each string.
    Parameters
    ----------
    pat : string
        Character sequence or regular expression
    case : boolean, default True
        If True, case sensitive
    flags : int, default 0 (no flags)
        re module flags, e.g. re.IGNORECASE
    regex : bool, default True
        If True use re.search, otherwise use Python in operator
    Returns
    """
    if regex:
        if not case:
            flags |= re.IGNORECASE

        regex = re.compile(pat, flags=flags)

        f = lambda x: bool(regex.search(attribute(x)))
    else:
        if case:
            f = lambda x: pat in attribute(x)
        else:
            upper_pat = pat.upper()
            f = lambda x: upper_pat in attribute(x).upper()
            # uppered = map(lambda x: x.upper(), arr)
            # return f
    return f


class Query(object):
    """
    Generic class that provides typed filtering capabilities
    """

    def __init__(self, _list: List):
        self._list = _list
        self._view = _list
        self._filters = []
        self._sorters = []
        self._sort_direction = []

    def new_view(self) -> 'Query':
        return Query(self._list)

    def get_list(self, clear=True):
        view = list(filter(lambda x: all(f(x) for f in self._filters), self._view))
        if len(self._sorters) == 1:
            view.sort(key=self._sorters[0])
        elif len(self._sorters) > 1 & all(self._sort_direction):
            view.sort(key=lambda x: tuple([f(x) for f in self._sorters]))
        else:
            sort_ = view
            for index, i in enumerate(self._sorters):
                sort_ = sorted(sort_, key=i, reverse=self._sort_direction[index])
            view = list(sort_)
        if clear:
            self._filters = []
            self._sorters = []
        return view

    def set_view(self):
        view = self.get_list(True)
        self._view = list(view)
        return self._view

    @str_to_attrgetter
    def group_by(self, attribute: (attrgetter, str)):
        item_list = self.get_list(clear=False)
        group_map = {}
        for item in item_list:
            index = attribute(item)
            items = group_map.get(index, [])
            items.append(item)
            group_map[index] = items
        return group_map

    @str_to_attrgetter
    def equals(self, attribute: (attrgetter, str), value):
        self._filters.append(lambda x: attribute(x) == value)
        return self

    @str_to_attrgetter
    def not_equals(self, attribute: (attrgetter, str), value):
        self._filters.append(lambda x: attribute(x) != value)
        return self

    @str_to_attrgetter
    def contains(self, attribute: (attrgetter, str), value, **kwargs):
        self._filters.append(str_contains(attribute, value, **kwargs))
        return self

    @str_to_attrgetter
    def is_set(self, attribute: (attrgetter, str)):
        self._filters.append(lambda x: attribute(x) is not None)
        return self

    @str_to_attrgetter
    def is_not_set(self, attribute: (attrgetter, str)):
        self._filters.append(lambda x: attribute(x) is None)
        return self

    @str_to_attrgetter
    def is_true(self, attribute: (attrgetter, str)):
        self._filters.append(lambda x: attribute(x) is True)
        return self

    @str_to_attrgetter
    def is_false(self, attribute: (attrgetter, str)):
        self._filters.append(lambda x: attribute(x) is not True)
        return self

    @str_to_attrgetter
    def less_than(self, attribute: (attrgetter, str), value, equal_than=False):
        if equal_than:
            self._filters.append(lambda x: attribute(x) <= value)
            return self
        self._filters.append(lambda x: attribute(x) < value)
        return self

    @str_to_attrgetter
    def greater_than(self, attribute: (attrgetter, str), value, equal_than=False):
        if equal_than:
            self._filters.append(lambda x: attribute(x) >= value)
            return self
        self._filters.append(lambda x: attribute(x) > value)
        return self

    @str_to_attrgetter
    def sort_by(self, attribute: (attrgetter, str), ascending=True):
        self._sorters.append(attribute)
        self._sort_direction.append(ascending)
        return self
