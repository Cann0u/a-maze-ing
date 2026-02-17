import random
import curses as cs
import time

class MazeGenerator():
    def __init__(self, height: int, width: int):
        self.width = width
        self.height = height

    def break_wall(self, maze, pos, direc):
        for i in range(2):
            x, y = pos
            h, w = direc
            maze[x + h][y + w] = "⬜"
            pos = (x + h, y + w)
        return pos

    def maze_gen(self) -> list[list[int]]:
        height = self.height + self.height % 2 - 1
        width = self.width + self.width % 2 - 1
        maze = [["⬛" for j in range(width)] for i in range(height)]
        direc = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        end = False
        prev = [(1, 1)]
        curr = prev.pop()
        x, y = curr
        maze[x][y] = "⬜"
        screen = cs.initscr()
        while not end:
            valid_pos = []
            for i, j in direc:
                if (
                    i != 0
                    and curr[0] + i * 2 > 0
                    and curr[0] + i * 2 < height
                    and maze[curr[0] + i * 2][curr[1]] == "⬛"
                ):
                    valid_pos.append((i, j))
                if (
                    j != 0
                    and curr[1] + j * 2 > 0
                    and curr[1] + j * 2 < width
                    and maze[curr[0]][curr[1] + j * 2] == "⬛"
                ):
                    valid_pos.append((i, j))
            if len(valid_pos) == 0:
                curr = prev.pop()
            else:
                prev.append(curr)
                curr = self.break_wall(maze, curr, random.choice(valid_pos))
            if prev == []:
                end = True
            for i in maze:
                screen.addstr(''.join(i) + '\n')
            time.sleep(1/100)
            screen.refresh()
            screen.clear()
        return maze
