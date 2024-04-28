#!/usr/bin/env python3

def contains_char(string, char):
    """Checks if ``char`` is contained in the string ``string``. Returns True,
    if ``char`` is contained, and False otherwise.

    Args:
        string (str):
            The string that ``char`` is to be searched in.
        char (str):
            The character that is to be searched in ``string``. You may
            safely assume, that ``len(char) == 1`` holds the entire time.

    Returns:
        bool:
            True iff ``char`` is contained in ``string`` and False otherwise.
    """
    assert len(char) == 1

    for c in string:
        if c == char:
            return True
    return False


def is_palindrome(string):
    """Checks if ``string`` is a palindrome, i.e. is the same when read from
    left to right as well as right to left.

    Args:
        string (str):
            The string that should be a palindrome. Possible whitespaces
            (``\n``,``\t``,`` ``,``\r``) are to be removed from the string
            before checking if its a palindrome.

    Returns:
        bool:
            True iff ``string`` is a palindrome, False otherwise.
    """
    reverse = ""
    for c in string:
        if c == " ":
            continue

        reverse = c.lower() + reverse

    print(reverse)
    if string.lower().replace(" ", "") == reverse.lower():
        return True
    return False

def count_char_frequency(string):
    """Counts the frequency of the occuring characters in ``string``.

    Args:
        string (str):
            The string of which the character frequency is counted.

    Returns:
        Dict[str, int]:
            A dictionary containing the characters as keys and
            the number of occurences in ``string`` as values.
    """

    #INFORMATION FÜR MICH
    """
    myDict = {200:'OK', 404:'Not Found', 502:'Bad Gateway'} 
    
    for key, value in myDict.items():
        print(key, value)
    
    >>> 200 OK 
    >>> 404 Not Found
    >>> 502 Bad Gateway
    """

    char_frequency = {}

    for c in string:
        if c in char_frequency:
            char_frequency[c] += 1
        else:
            char_frequency[c] = 1
    return char_frequency

def first_non_repeating_char(string, repeating=True):
    """Returns the first non repreating character of the string ``string``, if
    there is one. Otherwise returns None. If ``repeating`` is equal to ``True``
    this function returns the first repeating character of the string
    ``string``.

    Args:
        string (str):
            The string of which the first (non) repeating character is
            returned.
        repeating (bool, *optional*=False):
            If this is set to ``True``, then the first repeating char is
            returned.

    Returns:
        Optional[str]:
            The first (non) repeating character of the string ``string`` or
            None, if it does not exist. It should hold, that whenever the
            return value is not equal to ``None``, it has a length of 1.
    """

    if len(string) == 1:
        if repeating:
            return None
        else:
            return string

    string_dic = count_char_frequency(string)

    smallest_value = float("inf")
    smallest_key = None

    check = 0
    for key, value in string_dic.items():
        if repeating:
            if value >= 2:
                smallest_key = key
                break
            else:
                continue

        if value < smallest_value:
            check = value
            smallest_value = value
            smallest_key = key

    if check == len(string):
        smallest_key = None

    return smallest_key

def rotate_string(string, left_rot, right_rot):
    """Rotates the given ``string`` by ``left_rot`` to the left and
    ``right_rot`` to the right.

    Args:
        string (str):
            The string that is to be rotated.
        left_rot (int):
            The amount of characters the string is to be rotated to the left.
        right_rot (int):
            The amount of characters the string is to be rotated to the right.

    Returns:
        str:
            The rotated string.

    Example:
        ``rotate_string("HELLO", 1, 3)`` should return ``"LOHEL"``.
    """

    assert len(string) >= right_rot - left_rot

    res = ""

    #left rot
    left = ""
    for i in range(left_rot, len(string), 1):
        left = left+string[i]
    for i in range(0, left_rot, 1):
        left = left+string[i]

    #right rot
    right = ""
    for i in range(len(left) - right_rot, len(left), 1):
        right += left[i]
    for i in range(0, len(left) - right_rot, 1):
        right += left[i]
        res = right

    return res


def rotationally_equivalent(string1, string2):
    """Checks if the strings are rotationally equivalent.

    Args:
        string1 (str):
            The first string to be checked.
        string2 (str):
            The second string to be checked.

    Returns:
        bool:
            True iff the strings are rotationally equivalent, False otherwise.
    """

    """""
    if len(string1) != len(string2):
        return False

    res = ""
    for i in string1:
        if i in string2:
            res += i

    if len(res) == len(string2):
        return True
    """
    if len(string1) != len(string2):
        return False


    double_string1 = string1 + string1
    if string2 in double_string1:
        return True
    else:
        return False

def main():
    """The Main-Function of the programme. Is executed whenever this file is
    executed at top level.

    Hier kann beliebiger Testcode stehen, der bei der Korrektur vollständig
    ignoriert wird.
    """
    #print(contains_char("Hallo", "o"))
    print(is_palindrome("never odd or even"))
    #print(count_char_frequency("Hallo"))
    #print(first_non_repeating_char("ggggg"))
    #print("MY LIST:")
    #print(rotate_string("HELLO", 1, 3))
    #print(rotate_string("TESTE", 1, 3))
    #print(rotationally_equivalent("Hallo","laloH"))

if __name__ == "__main__": main()
