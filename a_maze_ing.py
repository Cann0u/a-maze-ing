from mazegen import MazeGenerator
from pydantic import ValidationError
import sys
import curses as cs
import time


def output_maze(lines: list[str], start: tuple[int, int], end: tuple[int, int],
                path_find: str) -> None:
    with open("output_maze.txt", "w") as file:
        for line in lines:
            file.write(line + "\n")
        file.write("\n")
        file.write(f"{start[0]},{start[1]}\n")
        file.write(f"{end[0]},{end[1]}\n")
        file.write("".join(path_find) + "\n")


def parse_config(filename: str) -> dict[str, str]:
    read_file = {}
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            read_file[key] = value
        return read_file


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
                            path = generator.solver.solve(maze, self.__screen)
                            generator.clear_path(maze)
                        except ValueError as e:
                            print(e)
                    case 5:
                        try:
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
        cs.nocbreak()
        self.__screen.keypad(False)
        cs.echo()
        cs.endwin()
        hex_map = generator.convert_hex_maze(maze)
        output_maze(hex_map, generator.start_pos, generator.end_pos, path)


def main() -> None:
    av = sys.argv
    ac = len(av)
    if ac != 2:
        print("error arg")
        sys.exit(1)
    try:
        config = parse_config(av[1])
        height = int(config["HEIGHT"])
        width = int(config["WIDTH"])
        start_pos = tuple(map(int, config["ENTRY"].split(",")))
        end_pos = tuple(map(int, config["EXIT"].split(",")))
        generator = MazeGenerator(
            height=height, width=width, start_pos=start_pos, end_pos=end_pos
        )
        visu = Visualizer()
        visu.render(generator)
    except ValidationError as e:
        for error in e.errors():
            print(error["msg"])


main()
