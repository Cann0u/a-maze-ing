from typing import Protocol
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
            self.parent_i = 0
            self.parent_j = 0
            self.f = float("inf")
            self.g = float("inf")
            self.h = 0

    def calculate_h_value(self, row: int, col: int):
        return ((row - self.end[0]) ** 2 + (col - self.end[1]) ** 2) ** 0.5

    @staticmethod
    def is_valid(row: int, col: int, size: tuple[int, int]):
        return (
            (row >= 0) and (row < size[0]) and (col >= 0) and (col < size[1])
        )

    @staticmethod
    def is_unblocked(curr: tuple, maze: list, direc: tuple):
        x, y = curr
        d_x, d_y = tuple(map(lambda e: e // 2, direc))
        return (
            maze[x - d_x][y - d_y] == 1
            and maze[x - direc[0]][y - direc[1]] == 1
        )

    def is_destination(self, row: int, col: int):
        return row == self.end[0] and col == self.end[1]

    def trace_path(
        self, screen, cell_tab: list[list[Cells]], maze: list[list[int]]
    ):
        from mazegen import MazeGenerator

        path = []
        row = self.end[0]
        col = self.end[1]

        while not (
            cell_tab[row][col].parent_i == row
            and cell_tab[row][col].parent_j == col
        ):
            path.append((row, col))
            temp_row = cell_tab[row][col].parent_i
            temp_col = cell_tab[row][col].parent_j
            row = temp_row
            col = temp_col
        path.append((row, col))
        path.reverse()
        prev = path[0]
        direc = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        maze[prev[0]][prev[1]] = 3
        for coord in path[1:]:
            i, j = coord
            for vis in direc:
                if prev[0] + vis[0] == i and prev[1] + vis[1] == j:
                    maze[prev[0] + vis[0] // 2][prev[1] + vis[1] // 2] = 3
            maze[i][j] = 3
            MazeGenerator.print_maze(screen, maze)
            time.sleep(1 / 60)
            screen.refresh()
            prev = coord
        string = ""
        for i in path:
            string += f"-> {path} "
        screen.getch()

    def solve(self, screen, maze: list[list[int]]) -> list[list[int]]:
        heigth = len(maze)
        width = len(maze[0])
        print(f"{heigth} {width}")
        direc = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        x, y = self.end
        if x >= heigth or y >= width:
            return "coubeh"
        if maze[self.end[0]][self.end[1]] != 1:
            return "Invalid end"
        if self.start == self.end:
            return maze
        closed_cell = [[False for j in range(width)] for i in range(heigth)]
        cell_tab = [
            [self.Cells() for j in range(width)] for i in range(heigth)
        ]
        i, j = self.start
        cell_tab[i][j].parent_i = i
        cell_tab[i][j].parent_j = j
        cell_tab[i][j].g = 0
        cell_tab[i][j].f = 0
        cell_tab[i][j].h = 0
        cell_open = []
        heapq.heappush(cell_open, (0.0, i, j))
        end = False
        while len(cell_open) > 0:
            p = heapq.heappop(cell_open)
            i = p[1]
            j = p[2]
            closed_cell[i][j] = True
            for vis in direc:
                new_i = i + vis[0]
                new_j = j + vis[1]
                if (
                    self.is_valid(new_i, new_j, (heigth, width))
                    and self.is_unblocked((new_i, new_j), maze, vis)
                    and not closed_cell[new_i][new_j]
                ):
                    if self.is_destination(new_i, new_j):
                        end = True
                        cell_tab[new_i][new_j].parent_i = i
                        cell_tab[new_i][new_j].parent_j = j
                        print("The destination cell is found")
                        self.trace_path(screen, cell_tab, maze)
                        return maze
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
        if not end:
            print("j'ai pas trouve")
        return maze
