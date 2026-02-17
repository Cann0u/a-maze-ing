import random
import curses as cs
import time
from pydantic import BaseModel, Field, model_validator


class MazeGenerator(BaseModel):
    height: int
    width: int
    start: tuple[int, int] = Field(default=(1, 1))

    @model_validator(mode='after')
    def check_format(self) -> 'MazeGenerator':
        if self.height < 2 or self.width < 2:
            raise ValueError('invalid maze format')
        if not self.start:
            raise ValueError('invalid start position')
        return self

    def break_wall(self, maze, pos, direc):
        for _ in range(2):
            x, y = pos
            h, w = direc
            maze[x + h][y + w] = "⬜"
            pos = (x + h, y + w)
        return pos

    def maze_gen(self) -> list[list[int]]:
        height = self.height * 2 + 1
        width = self.width * 2 + 1
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

    def find_path_dfs(self, maze):
        height = self.height * 2 + 1
        width = self.width * 2 + 1
        # traget = 
        # visit_cellule = set()
        start_maze = [self.start]
        direc = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        while start_maze:
            currend_node = start_maze.pop()
        return find_path

    # def reconstruc_path(self):
    #     pass
