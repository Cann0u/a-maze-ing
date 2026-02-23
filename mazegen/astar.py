from typing import Protocol
from constant import CELL
import heapq
import time


class MazeSolver(Protocol):
    def solve(self, maze: list[list[int]]) -> list[list[int]]:
        pass


class AStar:
    def __init__(self, start: tuple[int, int], end: tuple[int, int]):
        self.start = tuple(map(lambda e: e * 2 + 1, start))
        self.end = tuple(map(lambda e: e * 2 + 1, end))

    class Cells:
        def __init__(self):
            self.parent_i = -1
            self.parent_j = -1
            self.f = float("inf")
            self.g = float("inf")
            self.h = 0

    def calculate_h_value(self, row: int, col: int):
        return ((row - self.end[0]) ** 2 + (col - self.end[1]) ** 2) ** 0.5

    @staticmethod
    def is_valid(row: int, col: int, size: tuple[int, int]):
        return (row >= 0) and (row < size[0]) and (col >= 0) and (col < size[1])

    @staticmethod
    def is_unblocked(curr: tuple, maze: list, direc: tuple):
        x, y = curr
        d_x, d_y = tuple(map(lambda e: e // 2, direc))
        return (
            maze[x - d_x][y - d_y] != 0
            and maze[x - direc[0]][y - direc[1]] != CELL.WALL.value
        )

    def is_destination(self, row: int, col: int):
        return row == self.end[0] and col == self.end[1]

    def trace_path(self, screen, cell_tab: list[list[Cells]], maze: list[list[int]]):
        from mazegen import MazeGenerator

        path = []
        row = self.end[0]
        col = self.end[1]
        moove_matrix = {(-2, 0): "N", (2, 0): "S", (0, -2): "W", (0, 2): "E"}
        while not (
            cell_tab[row][col].parent_i == row and cell_tab[row][col].parent_j == col
        ):
            path.append((row, col))
            temp_row = cell_tab[row][col].parent_i
            temp_col = cell_tab[row][col].parent_j
            row = temp_row
            col = temp_col
        path.append((row, col))
        path.reverse()
        path_coord = []
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            move = (x2 - x1, y2 - y1)
            if move in moove_matrix:
                path_coord.append(moove_matrix[move])
                pos_x = (x1 + x2) // 2
                pos_y = (y1 + y2) // 2
                maze[pos_x][pos_y] = CELL.FIND.value
                if maze[x2][y2] == CELL.PATH.value:
                    maze[x2][y2] = CELL.FIND.value
            if screen is not None:
                MazeGenerator.print_maze(screen, maze)
                time.sleep(1 / 60)
                screen.refresh()
        return path_coord

    def solve(self, maze: list[list[int]], screen=None) -> list[int]:
        from mazegen import MazeGenerator

        height = len(maze)
        width = len(maze[0])
        direc = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        maze[self.start[0]][self.start[1]] = CELL.START.value
        x, y = self.end
        if x >= height or y >= width:
            raise ValueError("Invalid end coordinate")
        if (
            maze[self.end[0]][self.end[1]] != CELL.EMPTY.value
            and maze[self.end[0]][self.end[1]] != CELL.EXIT.value
        ):
            raise ValueError("Invalid end coordinate")
        if self.start == self.end:
            return maze
        maze[x][y] = 7
        closed_cell = [[False for j in range(width)] for i in range(height)]
        cell_tab = [[self.Cells() for j in range(width)] for i in range(height)]
        i, j = self.start
        cell_tab[i][j].parent_i = i
        cell_tab[i][j].parent_j = j
        cell_tab[i][j].g = 0
        cell_tab[i][j].f = 0
        cell_tab[i][j].h = 0
        cell_open = []
        heapq.heappush(cell_open, (0.0, i, j))
        while len(cell_open) > 0:
            p = heapq.heappop(cell_open)
            i = p[1]
            j = p[2]
            closed_cell[i][j] = True
            for vis in direc:
                new_i = i + vis[0]
                new_j = j + vis[1]
                if (
                    self.is_valid(new_i, new_j, (height, width))
                    and self.is_unblocked((new_i, new_j), maze, vis)
                    and not closed_cell[new_i][new_j]
                ):
                    maze[i + vis[0] // 2][j + vis[1] // 2] = CELL.PATH.value
                    if maze[new_i][new_j] != CELL.EXIT.value:
                        maze[new_i][new_j] = CELL.PATH.value
                    if self.is_destination(new_i, new_j):
                        cell_tab[new_i][new_j].parent_i = i
                        cell_tab[new_i][new_j].parent_j = j
                        return self.trace_path(screen, cell_tab, maze)
                    else:
                        g_new = cell_tab[i][j].g + 1.0
                        h_new = self.calculate_h_value(new_i, new_j)
                        f_new = g_new + h_new
                        if (
                            cell_tab[new_i][new_j].f == float("inf")
                            or cell_tab[new_i][new_j].f > f_new
                        ):
                            heapq.heappush(cell_open, (f_new, new_i, new_j))
                            cell_tab[new_i][new_j].f = f_new
                            cell_tab[new_i][new_j].g = g_new
                            cell_tab[new_i][new_j].h = h_new
                            cell_tab[new_i][new_j].parent_i = i
                            cell_tab[new_i][new_j].parent_j = j
                    if screen is not None:
                        MazeGenerator.print_maze(screen, maze)
                        time.sleep(1 / 60)
                        screen.refresh()
        return []
