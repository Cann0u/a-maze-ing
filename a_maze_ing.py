from mazegen import MazeGenerator
import curses as cs


def main() -> None:
    generator = MazeGenerator((9, 10), 20, 20)
    try:
        maze = cs.wrapper(generator.maze_gen)
    except ValueError as e:
        print(e)

main()
