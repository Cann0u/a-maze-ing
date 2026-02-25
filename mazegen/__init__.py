from typing import Any, List, Tuple
from pydantic import BaseModel, Field, model_validator
from .dfs_path import DFS
from constant import CELL
from .astar import AStar
import curses as cs
import random
import time


class MazeGenerator(BaseModel):
    height: int = Field(ge=2, default=2)
    width: int = Field(ge=2, default=2)
    start_pos: tuple[int, int] = Field(default=(0, 0))
    end_pos: tuple[int, int] = Field(default=(1, 1))
    perfect: bool
    seed: int | None = None

    @property
    def solver_astar(self) -> "AStar":
        return AStar(self.start_pos, self.end_pos)

    @property
    def solver_dfs(self) -> "DFS":
        return DFS(self.start_pos, self.end_pos)

    @property
    def start(self) -> Tuple[int, int]:
        return (self.start_pos[1] * 2 + 1, self.start_pos[0] * 2 + 1)

    @property
    def end(self) -> Tuple[int, int]:
        return (self.end_pos[1] * 2 + 1, self.end_pos[0] * 2 + 1)

    @model_validator(mode="after")
    def check_format(self) -> "MazeGenerator":
        if self.height < 2 or self.width < 2:
            raise ValueError("invalid maze format")
        if not self.start:
            raise ValueError("invalid start position")
        return self

    def break_wall(self, maze: List[List[int]], pos: Tuple[int, int],
                   direc: Tuple[int, int]) -> Tuple[int, int]:
        for _ in range(2):
            x, y = pos
            h, w = direc
            maze[x + h][y + w] = CELL.EMPTY.value
            pos = (x + h, y + w)
        return pos

    @staticmethod
    def setup_colors() -> None:
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
        for i, row in enumerate(maze):
            for j, col in enumerate(row):
                if col == CELL.FIND.value or col == CELL.PATH.value:
                    maze[i][j] = CELL.EMPTY.value

    @staticmethod
    def clear_path(maze: list[list[int]]) -> None:
        for i, row in enumerate(maze):
            for j, col in enumerate(row):
                if col == CELL.PATH.value:
                    maze[i][j] = CELL.EMPTY.value

    def set_fourty_two(self, maze: list[list[int]]) -> List[List[int]]:
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
        cs.start_color()
        cs.use_default_colors()
        func = {
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
            "cyan": 9
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
    def print_maze(screen: Any, maze: List[List[int]],
                   hide: bool = False) -> None:
        for y, row in enumerate(maze):
            for x, char in enumerate(row):
                if char == 0:
                    try:
                        screen.addstr(y, x * 2, "██", cs.color_pair(1))
                    except Exception:
                        pass
                elif char == 1:
                    try:
                        screen.addstr(y, x * 2, "██", cs.color_pair(2) |
                                      cs.A_BOLD)
                    except Exception:
                        pass
                elif char == 3:
                    try:
                        if hide:
                            screen.addstr(y, x * 2, "██", cs.color_pair(2) |
                                          cs.A_BOLD)
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
        height = self.height * 2 + 1
        width = self.width * 2 + 1
        maze = [[0 for j in range(width)] for i in range(height)]
        direc = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        x, y = self.end
        if (x >= height or y >= width) or (x < 0 or y < 0):
            raise ValueError("Invalid end coordinate")
        x, y = self.start
        if (x >= height or y >= width) or (x < 0 or y < 0):
            raise ValueError("Invalid start coordinate")
        end = False
        prev: List[Tuple[int, int]] = []
        self.set_fourty_two(maze)
        if maze[x][y] == 5:
            raise ValueError("Invalid start coordinate")
        x, y = self.end
        if maze[x][y] == 5:
            raise ValueError("Invalid end coordinate")
        curr = self.start
        x, y = curr
        maze[x][y] = 1
        while not end:
            valid_pos = []
            for i, j in direc:
                if (
                    i != 0
                    and curr[0] + i * 2 > 0
                    and curr[0] + i * 2 < height
                    and maze[curr[0] + i * 2][curr[1]] == CELL.WALL.value
                ):
                    valid_pos.append((i, j))
                if (
                    j != 0
                    and curr[1] + j * 2 > 0
                    and curr[1] + j * 2 < width
                    and maze[curr[0]][curr[1] + j * 2] == CELL.WALL.value
                ):
                    valid_pos.append((i, j))
            if len(valid_pos) == 0:
                curr = prev.pop()
            else:
                prev.append(curr)
                curr = self.break_wall(maze, curr, random.choice(valid_pos))
            if prev == []:
                end = True
            if screen is not None:
                self.print_maze(screen, maze)
                time.sleep(1 / 60)
                screen.refresh()
        if not self.perfect:
            for i in range(1, len(maze), 2):
                for j in range(1, len(maze[i]), 2):
                    if maze[i][j] == 1:
                        if (
                            height - 2 > i > 1
                            and 1 < j < width - 2
                            and random.randint(0, 100) <= 15
                        ):
                            y, x = random.choice(direc)
                            if (
                                maze[i + y * 2][j + x * 2] == CELL.EMPTY.value
                            ):
                                maze[i + y][j + x] = 1
            for i, row in enumerate(maze):
                for j, col in enumerate(row):
                    if (
                        height - 2 > i > 1
                        and 1 < j < width - 2
                    ):
                        if (
                            col == 0
                            and maze[i - 1][j] == CELL.EMPTY.value
                            and maze[i + 1][j] == CELL.EMPTY.value
                            and maze[i][j - 1] == CELL.EMPTY.value
                            and maze[i][j + 1] == CELL.EMPTY.value
                        ):
                            maze[i][j] = CELL.EMPTY.value
            if screen is not None:
                self.print_maze(screen, maze)
                time.sleep(1 / 60)
                screen.refresh()
        y, x = self.start
        maze[y][x] = 6
        maze[self.end[0]][self.end[1]] = CELL.EXIT.value
        return maze

    def convert_hex_maze(self, maze: list[list[int]]) -> list[str]:
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
