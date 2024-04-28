#!/usr/bin/env python3

"""
def factorial(n):
    result = 1
    for i in range(1, n+1):
        result *= i

    return result
"""

def my_exp(x):
    """Calculates an approximate value of the exponential function exp(x) of
    ``x``.

    Uses the Taylor-Series for the approximation and stops if the value of
    the series does not change anymore.

    Args:
        x (float):
            An arbitrary floating point number.

    Returns:
        float:
            The value of exp(x) calculated by the use of the Taylor-Series.
    """

    """
    result1 = 0.0
    result2 = 0.0
    k = 0
    while True:
        result1 += (x ** k) / factorial(k)
        k += 1
        if result2 != result1:
            result2 = result1
            continue
        else:
            result1 += (x ** k) / factorial(k)
            if result1 == result2:
                k = k+100
                result1 += (x ** k) / factorial(k)
                if result1 == result2:
                    break
                continue
            else:
                continue
    return result1
    """


    if x < 0:
        x = -x
        inverse = True
    else:
        inverse = False

    res = 1
    sum = 1
    k = 1

    while 1e-10 < abs(res):
        res = res * (x / k)
        sum += res
        k += 1

    # its accurately to solve e^-25 as 1/e^25
    if inverse:
        return 1 / sum
    else:
        return sum

def diff1(f, x, h=1e-8):
    """Calculates an approximate value of the first derivative by using the
    *forward* differences formula.

    Args:
        f ():
            The function that should be differenciated.
        x (float):
            Point at which the derivative should be calculated.
        h (float, *optional*=``1e-8``):
            Stepsize, should be small, but not too small.

    Returns:
        float:
            Approximate Value of the derivate of ``f`` at ``x``.
    """
    return (f(x+h) - f(x)) / h


def diff2(f, x, h=1e-8):
    """Calculates an approximate value of the first derivative by using the
    *central* differences formula.

    Args:
        f ():
            The function that should be differenciated.
        x (float):
            Point at which the derivative should be calculated.
        h (float, *optional*=``1e-8``):
            Stepsize, should be small, but not too small.

    Returns:
        float:
            Approximate Value of the derivate of ``f`` at ``x``.
    """
    return (f(x+h) - f(x - h)) / (2*h)


def sqrt(x):
    """Calculates the approximate value of the square root of ``x``.

    Args:
        x (float):
            The value to be taken the square root of.

    Returns:
        float:
            Approximate Value of the square root of ``x``.
    """
    assert x >= 0

    if x == 0:
        return 0

    x_n = x  # Initialisierung von xn mit x als Startwert
    epsilon = 1e-15

    while abs(x_n ** 2 - x) > x * epsilon:
        x_n = 0.5 * (x_n + (x / x_n))

    return x_n


def main():
    """The Main-Function of the programme. Is executed whenever this file is
    executed at top level.

    Hier kann beliebiger Testcode stehen, der bei der Korrektur vollständig
    ignoriert wird.
    """
    print(my_exp(-3))
    print(sqrt(4.0))


if __name__ == "__main__": main()
