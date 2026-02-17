from mazegen import MazeGenerator
import curses as cs


def main() -> None:
    generator = MazeGenerator(50, 50)
    maze = generator.maze_gen()
    # screen = cs.initscr()
    # for i in maze:
    #     screen.addch("|")
    #     for j in i:
    #         if j == 0:
    #             screen.addch("⬛")
    #         else:
    #             screen.addch("⬜")
    #     screen.addch("|")
    #     screen.addch("\n")
    #     screen.refresh()
    # screen.clear()


main()
