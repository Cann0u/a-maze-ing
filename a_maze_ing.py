from mazegen import MazeGenerator
from pydantic import ValidationError
import curses as cs
import time
import os
import dotenv
import sys


def output_maze(
    lines: list[str],
    start: tuple[int, int],
    end: tuple[int, int],
    path_find: str,
) -> None:
    """
    Write maze data to an output file.

    Args:
        lines: A list of strings representing the maze grid lines.
        start: A tuple containing the (row, column) coordinates of the start position.
        end: A tuple containing the (row, column) coordinates of the end position.
        path_find: A string or sequence representing the path solution through the maze.

    Returns:
        None

    Writes the maze grid, start position, end position, and solution path to 'output_maze.txt'.
    """
    with open("output_maze.txt", "w") as file:
        for line in lines:
            file.write(line + "\n")
        file.write("\n")
        file.write(f"{start[0]},{start[1]}\n")
        file.write(f"{end[0]},{end[1]}\n")
        file.write("".join(path_find) + "\n")


def parse_config(filename: str) -> dict[str, str]:
    """
    Parse a configuration file and extract maze parameters.
    Loads environment variables from a .env file and validates them.
    Extracts and converts configuration values for maze height, width,
    entry/exit positions, seed, and perfect maze flag.
    Args:
        filename (str): Path to the .env configuration file to load.
    Returns:
        dict[str, str]: A dictionary containing parsed configuration with keys:
            - 'height' (int): Height of the maze
            - 'width' (int): Width of the maze
            - 'start_pos' (tuple[int, int]): Entry point coordinates
            - 'end_pos' (tuple[int, int]): Exit point coordinates
            - 'perfect' (bool): Whether to generate a perfect maze
            - 'seed' (int, optional): Random seed if specified in config
    Raises:
        ValueError: If HEIGHT or WIDTH are not valid integers
        ValueError: If ENTRY or EXIT coordinates cannot be parsed as integers
        ValueError: If PERFECT field is not 'True' or 'False'
    """
    if not dotenv.load_dotenv(filename):
        return
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
    seed = -1
    try:
        height = int(read_file["HEIGHT"])
    except ValueError:
        raise ValueError("[ERROR] HEIGHT must be integer value")
    try:
        width = int(read_file["WIDTH"])
    except ValueError:
        raise ValueError("[ERROR] WIDTH must be integer value")
    try:
        start_pos = tuple(map(int, read_file["ENTRY"].split(",")))
        end_pos = tuple(map(int, read_file["EXIT"].split(",")))
    except ValueError:
        raise ValueError("[ERROR] Invalid Value in tuple EXIT or ENTRY")
    if read_file["SEED"] is not None:
        seed = int(read_file["SEED"])
    try:
        if read_file["PERFECT"] is None or read_file["PERFECT"] not in [
            "True",
            "False",
        ]:
            raise ValueError("[ERROR] PERFECT field must be 'True' or 'False'")
        perfect = read_file["PERFECT"] == "True"
    except Exception:
        raise ValueError("[ERROR] PERFECT field must be 'True' or 'False'")
    dico = {
        "height": height,
        "width": width,
        "start_pos": start_pos,
        "end_pos": end_pos,
        "perfect": perfect,
    }
    if seed != -1:
        dico.update({"seed": seed})
    return dico


def update_ouput(generator: MazeGenerator, maze):
    hex_map = generator.convert_hex_maze(maze)
    short_path = ShortPath.shortest_path(generator, maze)
    if short_path:
        output_map = output_maze(
            hex_map, generator.start_pos, generator.end_pos, short_path
        )
    return output_map


class Button:
    def __init__(self, coord: tuple[int, int], text: str):
        cs.init_pair(10, cs.COLOR_WHITE, -1)
        cs.init_pair(11, cs.COLOR_BLACK, cs.COLOR_WHITE)
        self.x, self.y = coord
        self.text = f"  {text}  "
        self.width = len(self.text)
        self.color_pair = cs.color_pair(10)
        self.focus = cs.color_pair(11)
        self.focused = False

    def draw(self, screen):
        if self.focused:
            screen.addstr(self.x, self.y, self.text, self.focus | cs.A_BOLD)
        else:
            screen.addstr(
                self.x, self.y, self.text, self.color_pair | cs.A_BOLD
            )

    def toggle_focus(self):
        self.focused = not self.focused


class Visualizer:
    def __init__(
        self,
    ):
        self.__screen = cs.initscr()
        self.__screen.nodelay(True)

    @property
    def screen(self):
        return self.__screen

    def render(self, generator: MazeGenerator):
        cs.curs_set(0)
        cs.noecho()
        hide = False
        generator.setup_colors()
        try:
            maze = generator.maze_gen(self.__screen)
            generator.solver_astar.solve(maze, self.__screen)
            update_ouput(generator, maze)
            generator.clear_path(maze)
            self.__screen.refresh()
        except ValueError as e:
            print(e)
            return
        buttons = [
            Button((1, 1), "exit"),
            Button((1, 20), "clear"),
            Button((2, 1), "hide"),
            Button((2, 20), "color"),
            Button((3, 1), "astar"),
            Button((3, 20), "dfs"),
            Button((4, 1), "regen"),
        ]
        win = cs.newwin(len(buttons) + 1, 36, len(maze), 0)
        win.border()
        win.keypad(True)
        win.move(0, 12)
        try:
            win.addstr("A-MAZE-ING")
        except Exception:
            pass
        select = 0
        buttons[0].toggle_focus()
        while True:
            generator.print_maze(self.__screen, maze, hide)
            for but in buttons:
                try:
                    but.draw(win)
                except Exception:
                    pass
            self.__screen.refresh()
            char = win.getch()
            old_select = select
            if char == cs.KEY_UP:
                select = (select - 2) % len(buttons)
            elif char == cs.KEY_RIGHT:
                select = (select + 1) % len(buttons)
            elif char == cs.KEY_LEFT:
                select = (select - 1) % len(buttons)
            elif char == cs.KEY_DOWN:
                select = (select + 2) % len(buttons)
            elif char in [10, 13, cs.KEY_ENTER]:
                match select:
                    case 0:
                        break
                    case 1:
                        generator.clear(maze)
                    case 2:
                        hide = not hide
                    case 3:
                        generator.change_color(maze)
                    case 4:
                        try:
                            generator.clear(maze=maze)
                            generator.solver_astar.solve(maze, self.__screen)
                            update_ouput(generator, maze)
                            generator.clear_path(maze)
                        except ValueError as e:
                            print(e)
                    case 5:
                        try:
                            generator.clear(maze=maze)
                            generator.solver_dfs.solve(maze, self.__screen)
                            update_ouput(generator, maze)
                            generator.clear_path(maze)
                        except ValueError as e:
                            print(e)
                    case 6:
                        maze = generator.maze_gen(self.__screen)
                        generator.solver_astar.solve(maze, self.__screen)
                        update_ouput(generator, maze)
                        generator.clear_path(maze)
            if old_select != select:
                buttons[old_select].toggle_focus()
                buttons[select].toggle_focus()
            win.border()
            win.move(0, 12)
            try:
                win.addstr("A-MAZE-ING")
            except Exception:
                pass
            win.refresh()
            self.__screen.refresh()
            time.sleep(1 / 60)
        print(generator.width)
        print(generator.height)
        win.keypad(False)
        win.clear()
        win.refresh()
        hex_map = generator.convert_hex_maze(maze)
        try:
            output_maze(hex_map, generator.start_pos, generator.end_pos)
        except Exception:
            pass
        update_ouput(generator, maze)

    def close_screen(self):
        cs.nocbreak()
        self.__screen.keypad(False)
        cs.echo()
        cs.endwin()


class ShortPath:

    @staticmethod
    def shortest_path(generator: MazeGenerator, maze):
        try:
            generator.clear_path(maze)
            astar_path = generator.solver_astar.solve(maze)
            shortest = astar_path
        except ValueError:
            print("path is invalid")
        return shortest


def main() -> None:
    av = sys.argv
    ac = len(av)
    if ac != 2:
        print("error arg")
        sys.exit(1)
    try:
        config = parse_config(av[1])
        generator = MazeGenerator(**config)
        visu = Visualizer()
        visu.render(generator)
        visu.close_screen()
        print(config)
    except (ValidationError, ValueError) as e:
        if isinstance(e, ValueError):
            print(e)
        else:
            for error in e.errors():
                print(error["msg"])


main()
