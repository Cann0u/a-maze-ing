from pydantic import ValidationError
from mazegen import MazeGenerator
from typing import List, Any, Optional
import curses as cs
import time
import sys


def output_maze(
    lines: list[str],
    start: tuple[int, int],
    end: tuple[int, int],
    path_find: list[str],
) -> str:
    """
    Write maze data to an output file.

    Args:
        lines: A list of strings representing the maze grid lines.
        start: A tuple containing the (row, column)
        coordinates of the start position.
        end: A tuple containing the (row, column)
        coordinates of the end position.
        path_find: A string or sequence representing
        the path solution through the maze.

    Returns:
        list str

    Writes the maze grid, start position, end position,
    and solution path to 'output_maze.txt'.
    """
    with open("output_maze.txt", "w") as file:
        for line in lines:
            file.write(line + "\n")
        file.write("\n")
        file.write(f"{start[0]},{start[1]}\n")
        file.write(f"{end[0]},{end[1]}\n")
        file.write("".join(path_find) + "\n")
        full_str = "\n".join(lines) + "\n\n"
        full_str += f"{start[0]},{start[1]}\n"
        full_str += f"{end[0]},{end[1]}\n"
        full_str += "".join(path_find) + "\n"
    return full_str


def update_output(
    generator: MazeGenerator, maze: List[List[int]]
) -> Optional[str]:
    """
    Update the maze output with the shortest path visualization.

    Parameters
    ----------
    generator : MazeGenerator
        The maze generator instance containing start and end positions.
    maze : List[List[int]]
        The maze structure represented as a 2D list of integers.

    Returns
    -------
    Optional[str]
        A string representation of the maze with the shortest path marked,
        or None if no path exists or output_map is not generated.

    Notes
    -----
    This function converts the maze to hexadecimal format, computes the
    shortest path, and generates a visual representation with the path
    marked on the maze.
    """
    hex_map = generator.convert_hex_maze(maze)
    short_path = ShortPath.shortest_path(generator, maze)
    if short_path:
        output_map = output_maze(
            hex_map, generator.start_pos, generator.end_pos, short_path
        )
    return output_map


class Button:
    """
    Button class for managing interactive UI elements in a curses-based
        interface.

    This class handles the creation, rendering, and focus state of clickable
    buttons with customizable text and color styling.

    Attributes
    ----------
    x : int
        The x-coordinate (row) position of the button on the screen.
    y : int
        The y-coordinate (column) position of the button on the screen.
    text : str
        The button label text with padding.
    width : int
        The width of the button text in characters.
    focused : bool
        Flag indicating whether the button currently has focus.
    color_pair : int
        The curses color pair attribute for unfocused state.
    focus : int
        The curses color pair attribute for focused state.

    Methods
    -------
    draw(screen)
        Renders the button on the provided curses window with appropriate
        styling.
    toggle_focus()
        Toggles the focus state of the button.
    """
    def __init__(self, coord: tuple[int, int], text: str):
        cs.init_pair(10, cs.COLOR_WHITE, -1)
        cs.init_pair(11, cs.COLOR_BLACK, cs.COLOR_WHITE)
        self.x, self.y = coord
        self.text = f"  {text}  "
        self.width = len(self.text)
        self.color_pair = cs.color_pair(10)
        self.focus = cs.color_pair(11)
        self.focused = False

    def draw(self, screen: Any) -> None:
        """
        Renders the button on the provided curses window with appropriate
        styling.
        """
        if self.focused:
            screen.addstr(self.x, self.y, self.text, self.focus | cs.A_BOLD)
        else:
            screen.addstr(
                self.x, self.y, self.text, self.color_pair | cs.A_BOLD
            )

    def toggle_focus(self) -> None:
        """
        Toggles the focus state of the button.
        """
        self.focused = not self.focused


class Visualizer:
    """
    Manages the graphical terminal interface using the curses library.

    This class is responsible for initializing the terminal screen, rendering
    the maze, setting up the interactive button menu, and handling user
    inputs (keyboard events) to trigger various actions like solving or
    regenerating the maze.
    """
    def __init__(
        self,
    ) -> None:
        """Initializes the curses screen and sets non-blocking input."""
        self.__screen = cs.initscr()
        self.__screen.nodelay(True)

    @property
    def screen(self) -> "cs.window":
        """
        Retrieves the underlying curses window object.

        Returns:
            cs.window: The primary curses screen object.
        """
        return self.__screen

    def render(self, generator: MazeGenerator) -> Any:
        """
        Starts the main event loop for the maze visualizer.

        This method generates the initial maze, sets up the UI components
        (buttons), and listens continuously for keyboard inputs to interact
        with the maze (e.g., changing colors, running A* or DFS solvers,
        clearing the board, or exiting).

        Args:
            generator (MazeGenerator): The main generator instance containing
                                       maze logic and solving algorithms.
        """
        cs.curs_set(0)
        cs.noecho()
        hide = False
        generator.setup_colors()
        try:
            maze = generator.maze_gen(self.__screen)
            generator.solver_astar.solve(maze, self.__screen)
            update_output(generator, maze)
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
                        generator.clear_all(maze)
                    case 2:
                        hide = not hide
                    case 3:
                        generator.change_color(maze)
                    case 4:
                        try:
                            hide = False
                            generator.clear_all(maze=maze)
                            generator.solver_astar.solve(maze, self.__screen)
                            generator.clear_path(maze)
                            self.__screen.refresh()
                        except ValueError as e:
                            print(e)
                    case 5:
                        try:
                            hide = False
                            generator.clear_all(maze=maze)
                            generator.solver_dfs.solve(maze, self.__screen)
                            generator.clear_path(maze)
                            self.__screen.refresh()
                        except ValueError as e:
                            print(e)
                    case 6:
                        hide = False
                        maze = generator.maze_gen(self.__screen)
                        generator.solver_astar.solve(maze, self.__screen)
                        update_output(generator, maze)
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
        update_output(generator, maze)

    def close_screen(self) -> None:
        """
        Safely shuts down the curses interface.

        Restores the terminal to its normal operating mode by turning off
        cbreak, disabling keypad mode, restoring echo, and ending the curses
        window session.
        """
        cs.nocbreak()
        self.__screen.keypad(False)
        cs.echo()
        cs.endwin()


class ShortPath:
    """
    Utility class for calculating the shortest path in a maze.
    """

    @staticmethod
    def shortest_path(
        generator: MazeGenerator, maze: List[List[int]]
    ) -> List[str]:
        """
        Calculates the shortest path using the A* algorithm.

        Args:
            generator (MazeGenerator): The generator containing the solver.
            maze (List[List[int]]): The 2D array representation of the maze.

        Returns:
            List[str]: A sequence representing the shortest path directions.
                       Returns an empty list or raises an exception internally
                       if no valid path is found.
        """
        try:
            generator.clear_path(maze)
            astar_path = generator.solver_astar.solve(maze)
            shortest: List[str] = astar_path
        except ValueError:
            print("path is invalid")
        return shortest


def main() -> None:
    """
    Main entry point for the maze generator script.

    Validates command-line arguments, initializes the maze generation
    configuration, and starts the curses visualizer. Catches and prints
    validation or value errors during execution.
    """
    av = sys.argv
    ac = len(av)
    if ac != 2:
        print("error arg")
        sys.exit(1)
    try:
        generator = MazeGenerator(av[1])
        visu = Visualizer()
        visu.render(generator)
        visu.close_screen()
    except (ValidationError, ValueError) as e:
        if isinstance(e, ValueError):
            print(e)
        else:
            for error in e.errors():
                print(error["msg"])


if __name__ == "__main__":
    main()
