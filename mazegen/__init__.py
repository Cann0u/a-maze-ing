from typing import Any, List, Tuple, Callable
from pydantic import BaseModel, Field, field_validator
from .dfs_path import DFS
from constant import CELL
from .astar import AStar
import curses as cs
import random
import time
import dotenv
import os


class Config(BaseModel):
    """
    Configuration model for maze generation settings.

    Attributes:
        height (int): The height of the maze. Must be >= 2. Defaults to 2.
            Alias: HEIGHT
        width (int): The width of the maze. Must be >= 2. Defaults to 2.
            Alias: WIDTH
        start_pos (tuple[int, int]): The entry point coordinates for the maze.
            Defaults to (0, 0). Alias: ENTRY
        end_pos (tuple[int, int]): The exit point coordinates for the maze.
            Defaults to (1, 1). Alias: EXIT
        perfect (bool): Flag indicating whether to generate a perfect maze.
            Alias: PERFECT
        seed (int | None): Optional seed value
                for maze generation reproducibility.
            Defaults to None. Alias: SEED
        out_put (str): The output file path for the generated maze.
            Must have minimum length of 1. Alias: OUTPUT_FILE

    Methods:
        tupl_valid(value: str) -> list[str]: Validator that converts string
            representation of tuples into a list of string coordinates.
            Removes parentheses and splits by comma.
    """

    height: int = Field(alias="HEIGHT", ge=2, default=2)
    width: int = Field(alias="WIDTH", ge=2, default=2)
    start_pos: tuple[int, int] = Field(alias="ENTRY", default=(0, 0))
    end_pos: tuple[int, int] = Field(alias="EXIT", default=(1, 1))
    perfect: bool = Field(alias="PERFECT")
    seed: int | None = Field(default=None, alias="SEED")
    out_put: str = Field(alias="OUTPUT_FILE", min_length=1)

    @field_validator("start_pos", "end_pos", mode="before")
    @staticmethod
    def tupl_valid(value: str) -> list[str]:
        """
        Parses a string representation of a tuple by
                removing empty parentheses and splitting by commas.

        Args:
            value (str): A string containing tuple-like
                data, potentially with parentheses.

        Returns:
            list[str]: A list of string elements split
                by commas after removing empty parentheses.

        Example:
            >>> tupl_valid("(1, 2, 3)")
            ['1', ' 2', ' 3']
            >>> tupl_valid("a,b,c")
            ['a', 'b', 'c']
        """
        value = value.replace("()", "")
        return value.split(",")


class MazeGenerator:
    """
    MazeGenerator class for creating and manipulating
        mazes using depth-first search algorithm.

    This class generates mazes based on configuration
        parameters, supports both perfect and
    non-perfect maze generation, includes pathfinding
        capabilities using A* and DFS algorithms,
    and provides visualization support through curses library.

    Attributes:
        start_pos (tuple[int, int]): Entry point coordinates in grid units.
        end_pos (tuple[int, int]): Exit point coordinates in grid units.
        width (int): Width of the maze in grid units.
        height (int): Height of the maze in grid units.
        start (tuple[int, int]): Entry point coordinates
            in maze array units (scaled by 2).
        end (tuple[int, int]): Exit point coordinates
                in maze array units (scaled by 2).
        seed (int, optional): Random seed for maze generation reproducibility.
        perfect (bool): Flag indicating whether to
            generate a perfect maze (no loops).
        solver_astar (AStar): A* pathfinding solver instance.
        solver_dfs (DFS): Depth-first search solver instance.
        maze (list[list[int]]): 2D list representing
            the generated maze structure.
        path (list): Solution path from start
            to end position found by A* solver.

        ValueError: If neither filename nor config is provided,
            or if configuration parameters are
                        invalid (height < 2, width < 2, invalid positions).
    """

    def __init__(self, filename: str = None, config: Config = None):
        if filename:
            parsed = self.parse_config(filename)
            config = Config(**parsed)
        elif not config:
            raise ValueError("Invalid config")
        self.start_pos = config.start_pos
        self.end_pos = config.end_pos
        self.width = config.width
        self.height = config.height
        self.start = (config.start_pos[1] * 2 + 1, config.start_pos[0] * 2 + 1)
        self.end = (config.end_pos[1] * 2 + 1, config.end_pos[0] * 2 + 1)
        self.seed = config.seed
        self.perfect = config.perfect
        self.solver_astar = AStar(config.start_pos, config.end_pos)
        self.solver_dfs = DFS(config.start_pos, config.end_pos)
        self.maze: list[list[int]] = self.maze_gen()
        self.path = self.solver_astar.solve(self.maze)
        self.clear_all(self.maze)

    @staticmethod
    def parse_config(filename: str) -> dict[str, Any]:
        """
        Parse a configuration file and extract maze parameters.
        Loads environment variables from a .env file and validates them.
        Extracts and converts configuration values for maze height, width,
        entry/exit positions, seed, and perfect maze flag.
        Args:
            filename (str): Path to the .env configuration file to load.
        Returns:
            dict[str, Any]:
            A dictionary containing parsed configuration with keys:
                - 'height' (int): Height of the maze
                - 'width' (int): Width of the maze
                - 'start_pos' (tuple[int, int]): Entry point coordinates
                - 'end_pos' (tuple[int, int]): Exit point coordinates
                - 'perfect' (bool): Whether to generate a perfect maze
                - 'seed' (int, optional): Random seed if specified in config
        Raises:
            ValueError: If HEIGHT or WIDTH are not valid integers
            ValueError:
            If ENTRY or EXIT coordinates cannot be parsed as integers
            ValueError: If PERFECT field is not 'True' or 'False'
        """
        if not dotenv.load_dotenv(filename):
            return {}
        key = [
            "HEIGHT",
            "WIDTH",
            "ENTRY",
            "EXIT",
            "PERFECT",
            "SEED",
            "OUTPUT_FILE",
        ]
        read_file = {j: os.getenv(j) for j in key}
        return read_file

    def break_wall(
        self,
        maze: List[List[int]],
        pos: Tuple[int, int],
        direc: Tuple[int, int],
    ) -> Tuple[int, int]:
        """
        Break through walls in the maze by moving in a specified direction.

        This method removes walls from the maze
            by traversing two cells in the given
        direction and marking them as empty cells.

        Args:
            maze (List[List[int]]): The maze grid where walls are to be broken.
            pos (Tuple[int, int]): The current position (x, y) in the maze.
            direc (Tuple[int, int]): The direction vector (h, w)
                to move and break walls.

        Returns:
            Tuple[int, int]: The new position after breaking through two walls.
        """
        for _ in range(2):
            x, y = pos
            h, w = direc
            maze[x + h][y + w] = CELL.EMPTY.value
            pos = (x + h, y + w)
        return pos

    @staticmethod
    def setup_colors() -> None:
        """
        Initialize and configure color pairs for curses terminal display.

        Sets up 7 color pairs with different foreground
            colors and a transparent
        background (-1). This function must be called
            after initializing the curses
        window to enable colored text output.

        Color pairs initialized:
        - Pair 1: Bright Black (8)
        - Pair 2: White (7)
        - Pair 3: Bright Blue (9)
        - Pair 4: Yellow (6)
        - Pair 5: Green (2)
        - Pair 6: Red (4)
        - Pair 7: Bright Cyan (11)

        Returns:
            None
        """
        cs.start_color()
        cs.use_default_colors()
        cs.init_pair(1, 8, -1)
        cs.init_pair(2, 7, -1)
        cs.init_pair(3, 9, -1)
        cs.init_pair(4, 6, -1)
        cs.init_pair(5, 2, -1)
        cs.init_pair(6, 4, -1)
        cs.init_pair(7, 11, -1)

    @staticmethod
    def clear_all(maze: list[list[int]]) -> None:
        """
        Clear all path and find markers from the maze.

        This function iterates through the maze and resets all cells
            marked as PATH or FIND
        back to EMPTY, effectively clearing the solution path while
            preserving walls and
        other maze structure.

        Args:
            maze (list[list[int]]): A 2D list representing the
                maze where each cell contains an integer value corresponding
                    to a CELL type.

        Returns:
            None: Modifies the maze in-place.
        """
        for i, row in enumerate(maze):
            for j, col in enumerate(row):
                if col == CELL.FIND.value or col == CELL.PATH.value:
                    maze[i][j] = CELL.EMPTY.value

    @staticmethod
    def clear_path(maze: list[list[int]]) -> None:
        """
        Clears the path in the given maze by replacing all path cells with
            empty cells.

        Args:
            maze (list[list[int]]): A 2D list representing the maze, where
                each cell is an integer. The value of CELL.PATH.value
                indicates a path cell, and CELL.EMPTY.value indicates
                an empty cell.

        Returns:
            None: This function modifies the maze in place and does not return
                a value.
        """
        for i, row in enumerate(maze):
            for j, col in enumerate(row):
                if col == CELL.PATH.value:
                    maze[i][j] = CELL.EMPTY.value

    def set_fourty_two(self, maze: list[list[int]]) -> List[List[int]]:
        """
        Embeds a predefined 42-shaped pattern into the center of the maze.

        This method takes a maze and overlays a hardcoded pattern (represented
            by 5s)
        at the center of the maze. The pattern is only applied if the maze
            dimensions are large enough to accommodate it without going out of
                bounds.

        Args:
            maze (list[list[int]]): A 2D list representing the maze where the
                pattern will be embedded.

        Returns:
            list[list[int]]: The modified maze with the 42-pattern embedded at
             the center, or the original maze unchanged if it's too small to
                fit the pattern.

        Note:
            - The pattern is a 11x15 grid containing 0s and 5s.
            - If a seed is set, it is applied before processing.
            - The method returns the original maze unmodified if its height or
                width is insufficient to accommodate the pattern.
        """
        fourty_two = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 0, 0, 0, 0, 0, 0, 0, 5, 0, 5, 0, 5, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 0, 5, 0, 5, 0, 0, 0, 5, 0, 5, 0, 5, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 5, 0, 5, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        height = self.height * 2 + 1
        width = self.width * 2 + 1
        if self.seed is not None:
            random.seed(self.seed)
        ft_height = len(fourty_two)
        ft_width = len(fourty_two[0])
        start = [
            int(self.height - (ft_height - self.height % 2) / 2),
            int(self.width - (ft_width - self.width % 2) / 2),
        ]
        if width <= ft_width:
            return maze
        if height <= ft_height:
            return maze
        for i, lst in enumerate(fourty_two):
            for j, val in enumerate(lst):
                maze[start[0] + i][start[1] + j] = val
        return maze

    @staticmethod
    def change_color(maze: list[list[int]]) -> None:
        """
        Change the color of different elements in a maze based on user input.

        This function initializes color pairs for walls, empty spaces, paths,
            and a finish token using the curses library. It creates a new
            window to receive user input for the key and color,
            updates the corresponding color pair, and handles exceptions if the
            input is invalid.

        Parameters:
            maze (list[list[int]]): A 2D list representing the maze structure.

        Returns:
            None
        """
        cs.start_color()
        cs.use_default_colors()
        func: dict[str, Callable[[int], None]] = {
            "wall": lambda e: cs.init_pair(1, e, -1),
            "empty": lambda e: cs.init_pair(2, e, -1),
            "path": lambda e: cs.init_pair(3, e, -1),
            "ft": lambda e: cs.init_pair(5, e, -1),
        }
        colors = {
            "grey": 8,
            "black": cs.COLOR_BLACK,
            "white": cs.COLOR_WHITE,
            "green": 2,
            "yellow": 11,
            "blue": 4,
            "cyan": 9,
        }
        win = cs.newwin(3, 45, len(maze) + 1, 35)
        win.border()
        cs.echo()
        win.move(1, 1)
        encode = win.getstr()
        string = encode.decode("utf-8")
        try:
            key, color = string.split(" ")[:2]
            win.addstr(f"{key}--{color}")
            fonc = func[key]
            fonc(colors[color])
        except Exception:
            pass
        win.clear()
        cs.noecho()
        win.refresh()

    @staticmethod
    def print_maze(
        screen: Any, maze: List[List[int]], hide: bool = False
    ) -> None:
        """
        Display a maze on a curses screen with color-coded characters.

        This function iterates through a 2D maze structure and renders each
        cell to the provided curses screen using colored block characters (██).
        Each integer value in the maze corresponds to a different color pair
        and represents different maze elements (walls, paths, start, end, etc.)

        Parameters
        ----------
        screen : Any
            A curses window object where the maze will be rendered.
        maze : List[List[int]]
            A 2D list representing the maze where each integer corresponds to
            a different maze element:
            - 0: Wall (color pair 1)
            - 1: Path (color pair 2, bold)
            - 3: Special element - hidden if hide=True, otherwise color pair 3
            - 4: Element (color pair 4)
            - 5: Element (color pair 5)
            - 6: Element (color pair 6)
            - 7: Element (color pair 7)
            - Other: Default element (color pair 3)
        hide : bool, optional
            If True, special elements (value 3) are rendered as paths
                (color pair 2).
            If False, special elements are rendered with color pair 3.
            Default is False.

        Returns
        -------
        None

        Notes
        -----
        - Rendering failures are silently ignored via exception handling.
        - Each maze cell is rendered at x position x*2 to account for
            character width.
        - A newline character is appended after each row.
        """
        for y, row in enumerate(maze):
            for x, char in enumerate(row):
                if char == 0:
                    try:
                        screen.addstr(y, x * 2, "██", cs.color_pair(1))
                    except Exception:
                        pass
                elif char == 1:
                    try:
                        screen.addstr(
                            y, x * 2, "██", cs.color_pair(2) | cs.A_BOLD
                        )
                    except Exception:
                        pass
                elif char == 3:
                    try:
                        if hide:
                            screen.addstr(
                                y, x * 2, "██", cs.color_pair(2) | cs.A_BOLD
                            )
                        else:
                            screen.addstr(y, x * 2, "██", cs.color_pair(3))
                    except Exception:
                        pass
                elif char == 4:
                    try:
                        screen.addstr(y, x * 2, "██", cs.color_pair(4))
                    except Exception:
                        pass
                elif char == 5:
                    try:
                        screen.addstr(y, x * 2, "██", cs.color_pair(5))
                    except Exception:
                        pass
                elif char == 6:
                    try:
                        screen.addstr(y, x * 2, "██", cs.color_pair(6))
                    except Exception:
                        pass
                elif char == 7:
                    try:
                        screen.addstr(y, x * 2, "██", cs.color_pair(7))
                    except Exception:
                        pass
                else:
                    try:
                        screen.addstr(y, x * 2, "██", cs.color_pair(3))
                    except Exception:
                        pass
                try:
                    screen.addch("\n")
                except Exception:
                    pass

    def maze_gen(self, screen: Any = None) -> list[list[int]]:
        """
        Generate a maze using depth-first search algorithm with optional
            imperfections.

        This method creates a maze by carving paths through a grid using a
        depth-first search approach. It supports both perfect mazes and mazes
        with loops. The maze is displayed in real-time if a screen object is
        provided.

        Parameters
        ----------
        screen : Any, optional
            A screen object for rendering the maze in real-time. If provided,
            the maze is displayed at 60 FPS during generation. Default is None.

        Returns
        -------
        list[list[int]]
            A 2D list representing the generated maze where:
            - 0 represents walls
            - 1 represents paths
            - 5 represents obstacles (set by set_fourty_two)
            - 6 represents the start position
            - CELL.EXIT.value represents the end position

        Raises
        ------
        ValueError
            If the start coordinate is outside the maze bounds or on an
            obstacle.
        ValueError
            If the end coordinate is outside the maze bounds or on an obstacle.

        Notes
        -----
        The maze dimensions are doubled to allow for wall placement between
        cells. If self.perfect is False, the algorithm adds random loops and
        removes isolated walls to create an imperfect maze. The start and end
        positions are marked with special values (6 and EXIT respectively)
        after maze generation.

        The algorithm uses a depth-first search with backtracking to ensure
        all cells are reachable, creating a spanning tree structure for
        perfect mazes.
        """
        height = self.height * 2 + 1
        width = self.width * 2 + 1
        self.maze = [[0 for j in range(width)] for i in range(height)]
        direc = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        x, y = self.end
        if (x >= height or y >= width) or (x < 0 or y < 0):
            raise ValueError("Invalid end coordinate")
        x, y = self.start
        if (x >= height or y >= width) or (x < 0 or y < 0):
            raise ValueError("Invalid start coordinate")
        end = False
        prev: List[Tuple[int, int]] = []
        self.set_fourty_two(self.maze)
        if self.maze[x][y] == 5:
            raise ValueError("Invalid start coordinate")
        x, y = self.end
        if self.maze[x][y] == 5:
            raise ValueError("Invalid end coordinate")
        curr = self.start
        x, y = curr
        self.maze[x][y] = 1
        while not end:
            valid_pos = []
            for i, j in direc:
                if (
                    i != 0
                    and curr[0] + i * 2 > 0
                    and curr[0] + i * 2 < height
                    and self.maze[curr[0] + i * 2][curr[1]] == CELL.WALL.value
                ):
                    valid_pos.append((i, j))
                if (
                    j != 0
                    and curr[1] + j * 2 > 0
                    and curr[1] + j * 2 < width
                    and self.maze[curr[0]][curr[1] + j * 2] == CELL.WALL.value
                ):
                    valid_pos.append((i, j))
            if len(valid_pos) == 0:
                curr = prev.pop()
            else:
                prev.append(curr)
                curr = self.break_wall(
                    self.maze, curr, random.choice(valid_pos)
                )
            if prev == []:
                end = True
            if screen is not None:
                self.print_maze(screen, self.maze)
                time.sleep(1 / 60)
                screen.refresh()
        if not self.perfect:
            for i in range(1, len(self.maze), 2):
                for j in range(1, len(self.maze[i]), 2):
                    if self.maze[i][j] == 1:
                        if (
                            height - 2 > i > 1
                            and 1 < j < width - 2
                            and random.randint(0, 100) <= 15
                        ):
                            y, x = random.choice(direc)
                            if (
                                self.maze[i + y * 2][j + x * 2]
                                == CELL.EMPTY.value
                            ):
                                self.maze[i + y][j + x] = 1
            for i, row in enumerate(self.maze):
                for j, col in enumerate(row):
                    if height - 2 > i > 1 and 1 < j < width - 2:
                        if (
                            col == 0
                            and self.maze[i - 1][j] == CELL.EMPTY.value
                            and self.maze[i + 1][j] == CELL.EMPTY.value
                            and self.maze[i][j - 1] == CELL.EMPTY.value
                            and self.maze[i][j + 1] == CELL.EMPTY.value
                        ):
                            self.maze[i][j] = CELL.EMPTY.value
            if screen is not None:
                self.print_maze(screen, self.maze)
                time.sleep(1 / 60)
                screen.refresh()
        y, x = self.start
        self.maze[y][x] = 6
        self.maze[self.end[0]][self.end[1]] = CELL.EXIT.value
        return self.maze

    def convert_hex_maze(self, maze: list[list[int]]) -> list[str]:
        """
        Convert a maze representation to hexadecimal format.

        This method transforms a maze structure into a list of hexadecimal
        strings, where each hex digit encodes the openings in four directions
        (up, right, down, left) using bit flags.

        Parameters
        ----------
        maze : list[list[int]]
            A 2D list representing the maze where 0 indicates an open passage
            and non-zero values indicate walls.

        Returns
        -------
        list[str]
            A list of strings, where each string contains hexadecimal
            characters representing the maze structure. Each hex digit encodes
            directional openings as follows:

            - Bit 0 (value 1): Top opening
            - Bit 1 (value 2): Right opening
            - Bit 2 (value 4): Bottom opening
            - Bit 3 (value 8): Left opening

        Notes
        -----
        The method iterates through odd-indexed positions in the maze to
        extract cell connectivity information and encodes it as hexadecimal
        values.
        """
        height = self.height * 2 + 1
        width = self.width * 2 + 1
        convert_line: List[str] = []
        for x in range(1, height, 2):
            row = []
            for y in range(1, width, 2):
                value = 0
                if maze[x - 1][y] == 0:
                    value |= 1
                if maze[x][y + 1] == 0:
                    value |= 2
                if maze[x + 1][y] == 0:
                    value |= 4
                if maze[x][y - 1] == 0:
                    value |= 8
                row.append(format(value, "X"))
            convert_line.append("".join(row))
        return convert_line
