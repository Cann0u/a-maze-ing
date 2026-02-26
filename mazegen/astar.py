from typing import Protocol, Tuple, List, Any, Optional
from constant import CELL
import heapq
import time


class MazeSolver(Protocol):
    """
    Protocol for maze solving algorithms.

    This protocol defines the interface that any maze solver implementation
    must follow.

    Methods
    -------
    solve(maze : list[list[int]]) -> list[list[int]]
        Solves the given maze and returns the solution path.

        Parameters
        ----------
        maze : list[list[int]]
            A 2D list representing the maze structure where each integer
            represents a cell type or state.

        Returns
        -------
        list[list[int]]
            A 2D list representing the solution path through the maze.
    """

    def solve(self, maze: list[list[int]]) -> list[list[int]]:
        pass


class AStar:
    start: Tuple[int, int]
    end: Tuple[int, int]

    def __init__(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        """
        Initialize the A* pathfinder with start and end coordinates.

        Parameters
        ----------
        start : tuple[int, int]
            The starting position as (row, col) in the maze grid.
        end : tuple[int, int]
            The ending position as (row, col) in the maze grid.

        Notes
        -----
        The coordinates are transformed by multiplying by 2 and adding 1,
        then swapped to convert from (row, col) to (col, row) format.
        """
        temp_start = tuple(map(lambda e: e * 2 + 1, start))
        temp_end = tuple(map(lambda e: e * 2 + 1, end))
        self.start = (temp_start[1], temp_start[0])
        self.end = (temp_end[1], temp_end[0])

    class Cells:
        """
        A class to represent a cell in the A* pathfinding algorithm.

        Attributes
        ----------
        parent_i : int
            The row index of the parent cell in the path. Initialized to -1.
        parent_j : int
            The column index of the parent cell in the path. Initialized to -1.
        f : float
            The total cost (f = g + h). Initialized to infinity.
        g : float
            The cost from the start node to the current cell. Initialized to
                infinity.
        h : float
            The heuristic estimated cost from the current cell to the goal.
            Initialized to 0.0.
        """

        def __init__(self) -> None:
            self.parent_i = -1
            self.parent_j = -1
            self.f = float("inf")
            self.g = float("inf")
            self.h = 0.0

    def calculate_h_value(self, row: int, col: int) -> float:
        """
        Calculate the heuristic value for A* pathfinding using Euclidean
            distance.

        This method computes the straight-line distance from a given position
        to the end position, which serves as the heuristic function (h-value)
        in the A* algorithm.

        Parameters
        ----------
        row : int
            The row coordinate of the current position.
        col : int
            The column coordinate of the current position.

        Returns
        -------
        float
            The Euclidean distance from the current position (row, col) to the
            end position (self.end[0], self.end[1]).
        """
        return float(
            float((row - self.end[0]) ** 2 + (col - self.end[1]) ** 2) ** 0.5
        )

    @staticmethod
    def is_valid(row: int, col: int, size: Tuple[int, int]) -> int:
        """
        Check if the given coordinates are within the bounds of a grid.

        Parameters
        ----------
        row : int
            The row coordinate to validate.
        col : int
            The column coordinate to validate.
        size : Tuple[int, int]
            A tuple containing (max_row, max_col) representing the grid
                dimensions.

        Returns
        -------
        int
            True if the coordinates are within bounds, False otherwise.
        """
        return (
            (row >= 0) and (row < size[0]) and (col >= 0) and (col < size[1])
        )

    @staticmethod
    def is_unblocked(
        curr: Tuple[int, int], maze: List[List[int]], direc: Tuple[int, int]
    ) -> bool:
        """
        Check if a path is unblocked between the current cell and a target
            direction.

        Parameters
        ----------
        curr : Tuple[int, int]
            The current position in the maze as (x, y) coordinates.
        maze : List[List[int]]
            The maze represented as a 2D list where each element represents a
            cell value.
        direc : Tuple[int, int]
            The direction vector as (dx, dy) to check for blockage.

        Returns
        -------
        bool
            True if the path is unblocked (both intermediate and target cells
                are not walls),
            False otherwise.
        """
        x, y = curr
        d_x, d_y = tuple(map(lambda e: e // 2, direc))
        return bool(
            maze[x - d_x][y - d_y] != 0
            and maze[x - direc[0]][y - direc[1]] != CELL.WALL.value
        )

    def is_destination(self, row: int, col: int) -> int:
        """
        Check if the given coordinates match the destination coordinates.

        Parameters
        ----------
        row : int
            The row coordinate to check.
        col : int
            The column coordinate to check.

        Returns
        -------
        int
            True if the coordinates match the destination, False otherwise.
        """
        return row == self.end[0] and col == self.end[1]

    def trace_path(
        self, screen: Any, cell_tab: list[list[Cells]], maze: list[list[int]]
    ) -> List[str]:
        """
        Trace the path from start to end cell and mark it in the maze.

        This method reconstructs the path by following parent pointers from
            the end cell back to the start cell, then converts the path into
            directional moves (N, S, E, W). The path is marked in the maze and
            optionally visualized on screen.

        Parameters
        ----------
        screen : Any
            The screen object for visualization. If None, visualization is
                skipped.
        cell_tab : list[list[Cells]]
            A 2D list of Cells representing the grid with parent pointers.
        maze : list[list[int]]
            A 2D list representing the maze where path cells will be marked
            with CELL.FIND.value.

        Returns
        -------
        List[str]
            A list of directional moves (N, S, E, W) representing the path from
            start to end cell.

        Notes
        -----
        The method updates the maze in-place, marking the path with
        CELL.FIND.value.
        If a screen is provided, the maze is rendered at 60 FPS during path
            tracing.
        """
        from mazegen import MazeGenerator

        path = []
        row = self.end[0]
        col = self.end[1]
        moove_matrix = {(-2, 0): "N", (2, 0): "S", (0, -2): "W", (0, 2): "E"}
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
                MazeGenerator.print_maze(screen, maze, hide=False)
                time.sleep(1 / 60)
                screen.refresh()
        return path_coord

    def solve(
        self, maze: list[list[int]], screen: Optional[Any] = None
    ) -> list[str]:
        from mazegen import MazeGenerator

        height = len(maze)
        width = len(maze[0])
        direc = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        closed_cell = [[False for j in range(width)] for i in range(height)]
        cell_tab = [
            [self.Cells() for j in range(width)] for i in range(height)
        ]
        i, j = self.start
        cell_tab[i][j].parent_i = i
        cell_tab[i][j].parent_j = j
        cell_tab[i][j].g = 0
        cell_tab[i][j].f = 0
        cell_tab[i][j].h = 0
        cell_open: List[Tuple[float, int, int]] = []
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
                        MazeGenerator.print_maze(screen, maze, hide=False)
                        time.sleep(1 / 60)
                        screen.refresh()
        return []
