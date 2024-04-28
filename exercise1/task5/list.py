#!/usr/bin/env python3

def first_and_last_element(l):
    """Checks if the first and last element of ``l`` are identical.

    Args:
        l (List):
            The given list to check.

    Returns:
        bool:
            True iff the first and last element of ``l`` are identical, False
            otherwise.
    """
    assert len(l) >= 1
    if l[0] == l[len(l)-1]:
        return True
    return False


def get_all_even_elements(l, start):
    """Returns all elements of ``l`` starting at ``start`` with an even index.

    Args:
        l (List):
            The list.
        start (int):
            Starting index, may be odd.

    Returns:
        List:
            List of all elements starting at ``start`` with an even index.
    """
    assert len(l) > start

    result = []
    for i in range(start, len(l)):
        if i % 2 == 0:
            result.append(l[i])

    return result



def get_last_two_elements(l):
    """Returns the last two elements of ``l`` in reverse order!

    Args:
        l (List):
            The list the last two elements are to be returned of. You may
            safely assume, that ``len(l) >= 2``.

    Returns:
        List:
            The last two elements of ``l``.

    Example:
        ``get_last_two_elements([1,2,3,4])`` should return ``[4, 3]``

    """
    assert len(l) >= 2
    res = []
    for i in range(len(l)-1, len(l)-3, -1):
        res.append(l[i])
    return res


def square_elements(number_list):
    """Squares all elements of the given list.

    Args:
        number_list (List[Numeric]):
            A list of numbers that is to be squared.

    Returns:
        List[Numeric]:
            List of the squared elements of ``number_list``.
    """
    res = []
    for i in range(0, len(number_list)):
        res.append(number_list[i] * number_list[i])
    return res


def filter_elements(list_one, list_two):
    """Filters all elements of ``list_one`` that are also in ``list_two``.

    Args:
        list_one (List):
            The first list.
        list_two (List):
            The second list.

    Returns:
        List:
            The filtered list.
    """

    res = []
    for i in list_one:
        if i in list_two:
            res.append(i)
    return res
    """
    res = []
    for i in range(0, len(list_one)):
        if list_one[i] in list_two:
            res.append(list_one[i])
    return res
    """

def select_elements(l, indices):
    """Selects all elements of ``l`` whose indices are in ``indices``.

    Args:
        l (List):
            The list the items should be selected from.
        indices (List[int]):
            The list of indices.

    Returns:
        List:
            The selected elements with indices in ``indices``.
    """
    res = []
    for i in range(0, len(l)):
        if i in indices:
            res.append(l[i])
            indices.remove(i)
    return res


def main():
    """The Main-Function of the programme. Is executed whenever this file is
    executed at top level.

    Hier kann beliebiger Testcode stehen, der bei der Korrektur vollständig
    ignoriert wird.
    """
    pass

if __name__ == "__main__": main()
