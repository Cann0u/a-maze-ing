from typing import List, Tuple, Set, Optional, Any
from constant import CELL
import time


class DFS:
    start: Tuple[int, int]
    end: Tuple[int, int]

    def __init__(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """
        Initialize the pathfinding instance with start and end coordinates.

        Parameters
        ----------
        start : Tuple[int, int]
            The starting coordinate as (row, col).
        end : Tuple[int, int]
            The ending coordinate as (row, col).

        Notes
        -----
        The input coordinates are transformed by multiplying by 2 and adding 1,
        then swapped to convert from (row, col) to (col, row) format.
        """
        temp_start = tuple(map(lambda e: e * 2 + 1, start))
        temp_end = tuple(map(lambda e: e * 2 + 1, end))
        self.start = (temp_start[1], temp_start[0])
        self.end = (temp_end[1], temp_end[0])

    def find_path_dfs(
        self, maze_matrix: List[List[int]], screen: Optional[Any] = None
    ) -> List[str]:
        """
        Find a path from start to end in a maze using Depth-First Search.

        This method implements a DFS algorithm to find a path through a maze
        represented as a 2D matrix. It explores the maze by following a
        stack-based approach, marking visited cells and updating the maze
        visualization in real-time if a screen is provided.

        Parameters
        ----------
        maze_matrix : List[List[int]]
            A 2D list representing the maze where different integer values
            denote different cell types (walls, empty cells, path markers, etc)
        screen : Optional[Any], optional
            A screen object for real-time visualization of the maze exploration
            If provided, the maze state is printed and the screen is refreshed
            at each step. Default is None.

        Returns
        -------
        List[str]
            A list of direction strings ('N', 'S', 'E', 'W') representing the
            path from the start position to the end position. Returns an empty
            list if no path is found.

        Notes
        -----
        The method modifies maze_matrix in-place to mark visited cells and the
        path. Cell values are checked against CELL enum values (WALL, EMPTY,
        FIND, PATH). The visualization updates at 60 FPS (1/60 second sleep
        between updates). Uses a stack data structure to maintain the frontier
        of unexplored cells.
        """
        from mazegen import MazeGenerator

        stack: List[Tuple[Tuple[int, int], List[str]]] = [((self.start), [])]
        is_visit: Set[Tuple[int, int]] = {self.start}
        moove_matrix = {(-1, 0): "N", (1, 0): "S", (0, -1): "W", (0, 1): "E"}
        while stack:
            current_node, current_path = stack.pop()
            if current_node == self.end:
                return current_path
            if screen is not None:
                MazeGenerator.print_maze(screen, maze_matrix)
                time.sleep(1 / 60)
                screen.refresh()
            for (m_x, m_y), direction in moove_matrix.items():
                pos_x = current_node[0] + m_x
                pos_y = current_node[1] + m_y
                if (
                    maze_matrix[pos_x][pos_y] == 1
                    or maze_matrix[pos_x][pos_y] == 3
                ):
                    maze_matrix[pos_x][pos_y] = 4
                if (
                    0 <= pos_x < len(maze_matrix)
                    and 0 <= pos_y < len(maze_matrix[0])
                    and maze_matrix[pos_x][pos_y] != CELL.WALL.value
                ):
                    if (pos_x, pos_y) not in is_visit:
                        is_visit.add((pos_x, pos_y))
                        if (
                            maze_matrix[pos_x][pos_y] == CELL.EMPTY.value
                            or maze_matrix[pos_x][pos_y] == CELL.FIND.value
                        ):
                            maze_matrix[pos_x][pos_y] = CELL.PATH.value
                        coord_path = current_path + [direction]
                        stack.append(((pos_x, pos_y), coord_path))
                        MazeGenerator.print_maze(screen, maze_matrix)
                        time.sleep(1 / 60)
                        if screen is not None:
                            screen.refresh()
        return []

    def solve(
        self, maze: List[List[int]], screen: Optional[Any] = None
    ) -> List[str]:
        """
        Solve the maze using depth-first search pathfinding.

        This method finds a path from the start position to the end position
        in a maze using depth-first search algorithm. It marks the path taken
        and optionally visualizes the solution on screen.

        Parameters
        ----------
        maze : List[List[int]]
            A 2D list representing the maze where each cell contains an integer
            value indicating the cell type (empty, wall, start, end, etc.).
        screen : Optional[Any], optional
            Optional screen object for visualization. If provided, the maze is
            redrawn after each move at 60 FPS. Default is None.

        Returns
        -------
        List[str]
            A list of direction strings ('N', 'S', 'E', 'W') representing the
            path from start to end. Returns an empty list if start and end are
            the same.

        Raises
        ------
        ValueError
            If the end coordinate is out of bounds or if the end cell is not
            empty or an exit cell.

        Notes
        -----
        This method modifies the input maze in-place, marking visited cells and
        the found path.
        """
        from mazegen import MazeGenerator

        height = len(maze)
        width = len(maze[0])
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
            # return maze
            return []
        maze[x][y] = 7
        path_dfs = self.find_path_dfs(maze, screen)
        x, y = self.start
        moove_matrix = {"N": (-1, 0), "S": (1, 0), "W": (0, -1), "E": (0, 1)}
        for coord in path_dfs:
            if maze[x][y] == CELL.PATH.value:
                maze[x][y] = CELL.FIND.value
            d_x, d_y = moove_matrix[coord]
            x += d_x
            y += d_y
            if screen is not None:
                MazeGenerator.print_maze(screen, maze)
                time.sleep(1 / 60)
                screen.refresh()
        return path_dfs
