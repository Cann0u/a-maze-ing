import random
import curses as cs
import time


class MazeGenerator:
    def __init__(self, start: tuple[int, int], height: int, width: int):
        self.width = width
        self.heigth = height
        x, y = start
        self.start = (x * 2 + 1, y * 2 + 1)

    def break_wall(self, maze, pos, direc):
        for i in range(2):
            x, y = pos
            h, w = direc
            maze[x + h][y + w] = 1
            pos = (x + h, y + w)
        return pos

    def setup_colors(self):
        cs.start_color()
        cs.use_default_colors()
        cs.init_pair(1, 8, -1)
        cs.init_pair(2, 7, -1)
        cs.init_pair(3, 9, -1)
        cs.init_pair(4, 6, -1)
        cs.init_pair(5, 1, -1)

    def set_fourty_two(self, maze: list[list[str]]):
        fourty_two = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 3, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 3, 0, 3, 0, 0, 0, 3, 0, 3, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 0, 0, 0, 3, 0, 3, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        heigth = self.heigth * 2 + 1
        width = self.width * 2 + 1
        ft_heigth = len(fourty_two)
        ft_width = len(fourty_two[0])
        start = [
            int(self.heigth - (ft_heigth - self.heigth % 2) / 2),
            int(self.width - (ft_width - self.width % 2) / 2)
        ]
        print(start)
        if width <= ft_width:
            return maze
        if heigth <= ft_heigth:
            return maze
        for i, lst in enumerate(fourty_two):
            for j, l in enumerate(lst):
                maze[start[0] + i][start[1] + j] = l

    def maze_gen(self, screen) -> list[list[int]]:
        heigth = self.heigth * 2 + 1
        width = self.width * 2 + 1
        maze = [[0 for j in range(width)] for i in range(heigth)]
        direc = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        end = False
        prev = []
        self.set_fourty_two(maze)
        curr = self.start
        if maze[curr[0]][curr[1]] != 0:
            raise ValueError("invalid start")
        x, y = curr
        maze[x][y] = 1
        self.setup_colors()
        while not end:
            valid_pos = []
            for i, j in direc:
                if (
                    i != 0
                    and curr[0] + i * 2 > 0
                    and curr[0] + i * 2 < heigth
                    and maze[curr[0] + i * 2][curr[1]] == 0
                ):
                    valid_pos.append((i, j))
                if (
                    j != 0
                    and curr[1] + j * 2 > 0
                    and curr[1] + j * 2 < width
                    and maze[curr[0]][curr[1] + j * 2] == 0
                ):
                    valid_pos.append((i, j))
            if len(valid_pos) == 0:
                curr = prev.pop()
            else:
                prev.append(curr)
                curr = self.break_wall(maze, curr, random.choice(valid_pos))
            if prev == []:
                end = True
            # for i in maze:
            #     screen.addstr(''.join(i) + '\n')
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
                    else:
                        try:
                            screen.addstr(y, x * 2, "██", cs.color_pair(3))
                        except Exception:
                            pass
                try:
                    screen.addch("\n")
                except Exception:
                    pass
            time.sleep(1 / 60)
            screen.refresh()
        screen.addstr("rentre une touche stp: ")
        screen.getch()
        screen.clear()
        # cs.nocbreak()
        # screen.keypad(False)
        # cs.echo()
        # cs.endwin()
        return maze
