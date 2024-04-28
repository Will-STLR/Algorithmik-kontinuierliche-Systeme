#!/usr/bin/env python3

import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.animation as animation


glider = np.array([[0,1,0],
                   [0,0,1],
                   [1,1,1]],
                  dtype=bool)


c10orthogonal = np.array([[0,1,1,0,0,1,1,0],
                          [0,0,0,1,1,0,0,0],
                          [0,0,0,1,1,0,0,0],
                          [1,0,1,0,0,1,0,1],
                          [1,0,0,0,0,0,0,1],
                          [0,0,0,0,0,0,0,0],
                          [1,0,0,0,0,0,0,1],
                          [0,1,1,0,0,1,1,0],
                          [0,0,1,1,1,1,0,0],
                          [0,0,0,0,0,0,0,0],
                          [0,0,0,1,1,0,0,0],
                          [0,0,0,1,1,0,0,0]],
                         dtype=bool)


def gamegrid(w, h, entities):
    """Creates the game grid on which the Game of Life is to be executed.

    Args:
        w (int): Width of the grid.
        h (int): Height of the grid.
        entities (List[Tuple[np.ndarray, int, int]]):
            List of start entities together with their initial positions that
            are to be placed at the specified position on the grid. You may
            safely assume, that the positional entries in the list do not
            break the boundaries of the game grid.

    Returns:
        np.ndarray: The game grid modelled as an (h, w) numpy-array of type
        ``bool``.
    """
    grid = np.zeros((h,w), dtype=bool)
    for (entity, x, y) in entities:
        add_entity(grid, entity, x, y)
    return grid

def add_entity(grid, entity, y, x):
    """Adds an ``entity`` to the given ``grid`` at the specified position.

    Args:
        grid (np.ndarray): The original game grid.
        entity (np.ndarray): The entity that should be added.
        y (int): The y-position the entity shall be added at.
        x (int): The x-position the entity shall be added at.

    Returns:
        np.ndarray: The updated game grid with the entity starting at position
        (y, x).
    """
    rows = len(entity)
    columns = len(entity[0])

    for i in range(rows):
        for j in range(columns):
            grid[y + i][x + j] = entity[i, j]

    return grid

def next_step(grid):
    """Updates the game grid ``grid`` according to the game rules.

    Args:
        grid (np.ndarray): The game grid.

    Returns:
        np.ndarray: The game grid after one time step. You can read the
        rules according to which you should update each cell in your
        exercise sheet.
    """
    rows, cols = grid.shape

    new_grid = grid.copy()

    for i in range(rows):
        for j in range(cols):
            alive_neighbors = 0

            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:

                    if x == 0 and y == 0:
                        continue

                    neighbor_i = (i + x) % rows
                    neighbor_j = (j + y) % cols

                    alive_neighbors += grid[neighbor_i, neighbor_j]

            if grid[i, j]:
                if alive_neighbors < 2 or alive_neighbors > 3:
                    new_grid[i, j] = 0
            else:
                if alive_neighbors == 3:
                    new_grid[i, j] = 1

    np.copyto(grid, new_grid)

    return grid

def gameoflife(grid):
    """Animates the Game of Life using Matplotlib.

    Args:
        grid (np.ndarray): The game grid with which the animation starts.
    """
    fig, ax = plt.subplots()
    mat = ax.matshow(grid, cmap=cm.gray_r)
    ani = animation.FuncAnimation(fig, lambda _: mat.set_data(next_step(grid)),
                                  frames=100,
                                  interval=50,
                                  blit=False)
    plt.show()



def main():
    """The Main-Function of the programme. Is executed whenever this file is
    executed at top level.

    Hier kann beliebiger Testcode stehen, der bei der Korrektur vollständig
    ignoriert wird.
    """
    grid = gamegrid(40, 40, [(glider, 13, 4),
                             (c10orthogonal, 25, 25)])
    gameoflife(grid)

if __name__ == "__main__": main()
