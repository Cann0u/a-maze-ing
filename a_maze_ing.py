from mazegen import MazeGenerator
from mazegen import AStar
import curses as cs


def main() -> None:
    generator = MazeGenerator((0, 0), 20, 20)
    screen = cs.initscr()
    try:
        maze = cs.wrapper(generator.maze_gen)
    except ValueError as e:
        print(e)
    solver = AStar((0, 0), (19, 19))
    solver.solve(maze, screen)


main()
