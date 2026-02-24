from mazegen import MazeGenerator
from pydantic import ValidationError
import sys
import curses as cs
import time
import os
import dotenv


def output_maze(
    lines: list[str],
    start: tuple[int, int],
    end: tuple[int, int],
    path_find: str,
) -> None:
    with open("output_maze.txt", "w") as file:
        for line in lines:
            file.write(line + "\n")
        file.write("\n")
        file.write(f"{start[0]},{start[1]}\n")
        file.write(f"{end[0]},{end[1]}\n")
        file.write("".join(path_find) + "\n")


def parse_config(filename: str) -> dict[str, str]:
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
    if read_file["PERFECT"] is None:
        raise ValueError("[ERROR] PERFECT field must be 'True' or 'False'")
    if read_file["SEED"] is not None:
        seed = int(read_file["SEED"])
    perfect = read_file["PERFECT"] == "True"
    dico = {"height": height,
            "width": width,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "perfect": perfect}
    if seed != -1:
        dico.update({"seed": seed})
    return dico


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
        path = []
        cs.curs_set(0)
        cs.noecho()
        self.__screen.keypad(True)

        try:
            maze = generator.maze_gen(self.__screen)
            path = generator.solver.solve(maze, self.__screen)
            generator.clear_path(maze)
        except ValueError as e:
            print(e)
            return
        buttons = [
            Button((len(maze), 0), "exit"),
            Button((len(maze), 20), "clear"),
            Button((len(maze) + 1, 0), "clear_path"),
            Button((len(maze) + 1, 20), "hide"),
            Button((len(maze) + 2, 0), "astar"),
            Button((len(maze) + 2, 20), "dfs"),
            Button((len(maze) + 3, 0), "regen"),
        ]
        hide = False
        select = 0
        buttons[0].toggle_focus()
        while True:
            for but in buttons:
                but.draw(self.__screen)
            char = self.__screen.getch()
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
                        generator.clear_path(maze)
                    case 3:
                        hide = not hide
                    case 4:
                        try:
                            generator.clear(maze=maze)
                            path = generator.solver.solve(maze, self.__screen)
                            generator.clear_path(maze)
                        except ValueError as e:
                            print(e)
                    case 5:
                        try:
                            generator.clear(maze=maze)
                            path = generator.solver_bis.solve(
                                maze, self.__screen
                            )
                            generator.clear_path(maze)
                        except ValueError as e:
                            print(e)
                    case 6:
                        maze = generator.maze_gen(self.__screen)
                        path = generator.solver.solve(maze, self.__screen)
                        generator.clear_path(maze)
            if old_select != select:
                buttons[old_select].toggle_focus()
                buttons[select].toggle_focus()
            generator.print_maze(self.__screen, maze, hide)
            self.__screen.refresh()
            time.sleep(1 / 60)
        print(generator.width)
        print(generator.height)
        hex_map = generator.convert_hex_maze(maze)
        output_maze(hex_map, generator.start_pos, generator.end_pos, path)

    def close_screen(self):
        cs.nocbreak()
        self.__screen.keypad(False)
        cs.echo()
        cs.endwin()


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
        print(config["PERFECT"])
    except (ValidationError, ValueError) as e:
        if isinstance(e, ValueError):
            print(e)
        else:
            for error in e.errors():
                print(error["msg"])


main()
