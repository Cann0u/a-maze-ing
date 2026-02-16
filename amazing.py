from mazegen import MazeGenerator
import curses as cs


def main() -> None:
    generator = MazeGenerator(20, 30)
    maze = generator.maze_gen()
    screen = cs.initscr()
    for i in maze:
        screen.addstr(i)
        screen.refresh()