#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def rotation_matrix(omega):
    """Calculates the classical 2D-rotation matrix with angle ``omega``.

    Args:
        omega (float): Rotation-Angle

    Returns:
        np.ndarray: The resulting rotation matrix of dimension (2, 2).
    """
    # INFO: Um eine Rotationsmatrix für einen gegebenen Winkel w zu erstellen, kannst man folgende Formel verwenden:
    """
    R = [cos(w)    −sin(w)
         sin(w)     cos(w)]     
    """

    cos_omega = np.cos(omega)
    sin_omega = np.sin(omega)

    return np.array([[cos_omega, -sin_omega],
                     [sin_omega, cos_omega]])

def reflection_matrix(omega):
    """Calculates the classical 2D-reflection matrix with angle ``omega``.

    Args:
        omega (float): Reflection-Angle

    Returns:
        np.ndarray: The resulting reflection matrix of dimension (2, 2).
    """

    # INFO: Um eine Rotationsmatrix für einen gegebenen Winkel w zu erstellen, kannst man folgende Formel verwenden:
    """
    R = [cos(2w)    sin(2w)
         sin(2w)     -cos(2w)]     
    """

    cos_2omega = np.cos(2 * omega)
    sin_2omega = np.sin(2 * omega)

    return np.array([[cos_2omega, sin_2omega],
                     [sin_2omega, -cos_2omega]])


def eye(n, m):
    """Determines an identity matrix, i.e. a matrix with ones on its diagonal and
    zeros everywhere else, of arbitrary shape.

    Args:
        n (int): Number of Rows
        m (int): Number of Columns

    Returns:
        np.ndarray: The resulting "identity matrix" of dimension (n, m).
    """
    # HILFREICHE FUNKTIONEN
    """
    # Erstelle eine leere Matrix mit der angegebenen Form
    result = np.zeros((n, m))

    # Setze die Diagonalelemente auf Einsen
    np.fill_diagonal(result, 1)
    """

    return np.eye(n, m)


def compose(*matrices):
    """Composes the given ``matrices`` to one single matrix.

    Args:
        matrices (List[np.ndarray]): Input matrices.

    Returns:
        np.ndarray: Composed Matrix.
    """
    assert matrices, "Expected at least one Matrix"

    result = matrices[0]
    for i in range(1, len(matrices)):
        result = np.dot(result, matrices[i])

    return result


def antidiag(values):
    """Calculates an antidiagonal matrix, i.e. a matrix where the entries are
    filled on the diagonal from bottom left to top right.

    Args:
        values (List[float]): The values on the antidiagonal.

    Returns:
        np.ndarray: The resulting quadratic matrix.

    Example:
        ``antidiag([2., 3.])`` should return the matrix
        ``[[0., 3.], [2., 0.]]``. So please fill the values from bottom left
        to top right.
    """
    assert len(values) >= 1

    n = len(values)
    result = np.zeros((n, n))

    for i in range(n):
        result[n-i-1][i] = values[i]

    return result



def vandermonde_matrix(values):
    """Generates a Vandermonde Matrix.

    Args:
        values (List[float]): Input values.

    Returns:
        np.ndarray: A quadratic matrix filled with the powers of the input
        values increasing from left to right columnwise.
    """
    assert len(values) >= 1
    #return np.column_stack([np.array(values) ** i for i in range(n)])
    n = len(values)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matrix[j][i] = values[j] ** i
    return matrix

def kronecker_product(A, B):
    """Calculates the Kronecker-Matrix-Product of ``A`` and ``B``.
    Args:
        A (np.ndarray): First Factor.
        B (np.ndarray): Second Factor.

    Warning:
        ``A`` as well as ``B`` might be multidimensional, i.e.
        ``len(shape(A))`` is **not** bounded from above!

    Returns:
        np.ndarray: The resulting matrix.
    """
    return np.kron(A, B)


def walsh_matrix(n):
    """Calculates the Walsh Matrix with index ``n``.

    Args:
        n (int): Determines the dimensions and contents of the Walsh-Matrix

    Returns:
        np.ndarray: The resulting matrix of dimension (2**n, 2**n).
    """
    if n == 0:
        return np.array([[1]])

    hadamard_base = np.array([[1, 1], [1, -1]])

    walsh = hadamard_base
    for _ in range(1, n):
        walsh = kronecker_product(hadamard_base, walsh)

    return walsh


def main():
    """The Main-Function of the programme. Is executed whenever this file is
    executed at top level.

    Hier kann beliebiger Testcode stehen, der bei der Korrektur vollständig
    ignoriert wird.
    """
    pass

if __name__ == "__main__": main()
