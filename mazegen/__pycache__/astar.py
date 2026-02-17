from typing import Protocol
import heapq


class MazeSolver(Protocol):
    def solve(self, maze: list[list[int]]) -> list[list[int]]:
        pass


class AStar:
    def __init__(self, start: tuple[int, int], end: tuple[int, int]):
        self.start = start
        self.end = end

    class Cells:
        def __init__(self):
            self.parent_i = 0
            self.parent_j = 0
            self.f = float("inf")
            self.g = float("inf")
            self.h = 0

    def solve(self, maze: list[list[int]]) -> list[list[int]]:
        heigth = len(maze)
        width = len(maze[0])

        if self.start == self.end:
            return maze
        closed_cell = [[False for j in width] for i in heigth]
        cell_tab = [[self.Cells() for j in width] for i in heigth]
        i, j = self.start
        cell_tab[i][j].f = 0
        cell_tab[i][j].g = 0
        cell_tab[i][j].f = 0
        cell_tab[i][j].parent_i = i
        cell_tab[i][j].parent_j = j
        maze[i][j] = 3
        cell_open = []
        

        return maze
