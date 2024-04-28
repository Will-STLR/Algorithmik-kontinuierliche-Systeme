#!/usr/bin/env python3

def is_prime(n):
    """Checks if the given number is prime.

    Args:
        n (int):
            Integer that should be checked.

    Returns:
        bool:
            True iff n is a prime number, False otherwise.
    """
    if n == 0 or n == 1: return False
    # TODO
    divisor = 2
    while divisor < n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True


def int2str(n, base):
    """Conversts an integer ``n`` into a string representation with respect
    to the basis ``base``.

    Args:
        n (int):
            Integer to be converted.
        base (int):
            With respect to which base the number should be represented.

    Returns:
        str:
            String representation of the number.
    """
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    assert 2 <= base <= 36, "Invalid base"
    # TODO
    if n == 0:
        return "0"

    result = ""
    while n > 0:
        digit = n % base
        result = digits[digit] + result
        n //= base

    return result


def is_emirp(n):
    """Checks if the interger ``n`` is an emirp-number, i.e. a prime that
    results in a different prime whenever you mirror its decimal representation.

    Args:
        n (int):
            Number to be checked.

    Returns:
        bool:
            True iff nis an emirp-number, False otherwise.
    """
    if not is_prime(n): return False
    # TODO

    emirp = int2str(n, 10)

    if len(emirp) == 1:
        return False

    reverse = ""
    for c in emirp:
        reverse = c + reverse

    check = int(reverse)
    if is_prime(check):
        return True

    return False

def main():
    """The Main-Function of the programme. Is executed whenever this file is
    executed at top level.

    Hier kann beliebiger Testcode stehen, der bei der Korrektur vollständig
    ignoriert wird.
    """
    # Beispiel:
    for n in [1, 2, 3, 4, 5, 6, 7, 97, 98, 99]:
        print("Ist " + str(n) + " eine Primzahl? " + str(is_prime(n)))


    # Beispiel:
    print("Mirpzahlen: ", end='')
    for n in range(99):
        if is_emirp(n):
            print(' ' + str(n), end='')


if __name__ == "__main__": main()
