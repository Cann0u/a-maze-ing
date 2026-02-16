import random


class MazeGenerator():
    def __init__(self, height: int, width: int):
        self.width = width
        self.height = height

    def break_wall(self, maze, pos, direc):
        for i in range(2):
            x, y = pos
            h, w = direc
            maze[x + h][y + w] = 0
            pos = (x + h, y + w)
        return pos

    def maze_gen(self) -> list[list[int]]:
        maze = [[1 for j in range(self.width)] for i in range(self.height)]
        direc = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        end = False
        prev = [(1, 1)]
        curr = prev.pop()
        while not end:
            valid_pos = []
            for i, j in direc:
                if (i != 0 and curr[0] + i * 2 > 0
                        and curr[0] + i * 2 < self.height
                        and maze[curr[0] + i * 2][curr[1]] == 1):
                    valid_pos.append((i, j))
                if (j != 0 and curr[1] + j * 2 > 0
                        and curr[1] + j * 2 < self.width
                        and maze[curr[0]][curr[1] + j * 2] == 1):
                    valid_pos.append((i, j))
            if len(valid_pos) == 0:
                curr = prev.pop()
            else:
                prev.append(curr)
                curr = self.break_wall(maze, curr, random.choice(valid_pos))
            if prev == []:
                end = True
        return maze
