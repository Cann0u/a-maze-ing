import time


class DFS:
    def __init__(self, start: tuple[int, int], end: tuple[int, int]):
        self.start = tuple(map(lambda e: e * 2 + 1, start))
        self.end = tuple(map(lambda e: e * 2 + 1, end))
        self.start = (self.start[1], self.start[0])
        self.end = (self.end[1], self.end[0])

    def find_path_dfs(self, maze_matrix, screen=None) -> bool:
        from mazegen import MazeGenerator

        stack = [(self.start, [])]
        is_visit = {self.start}
        moove_matrix = {(-1, 0): "N",
                        (1, 0): "S",
                        (0, -1): "W",
                        (0, 1): "E"}
        while stack:
            current_node, current_path = stack.pop()
            if current_node == self.end:
                return current_path
            if screen is not None:
                MazeGenerator.print_maze(screen, maze_matrix)
                time.sleep(1 / 60)
                screen.refresh()
            for (m_x, m_y), direction in moove_matrix.items():
                pos_x = current_node[0] + m_x
                pos_y = current_node[1] + m_y
                if (
                    maze_matrix[pos_x][pos_y] == 1
                    or maze_matrix[pos_x][pos_y] == 3
                ):
                    maze_matrix[pos_x][pos_y] = 4
                if (
                    0 <= pos_x < len(maze_matrix)
                    and 0 <= pos_y < len(maze_matrix[0])
                    and maze_matrix[pos_x][pos_y] != 0
                ):
                    if (pos_x, pos_y) not in is_visit:
                        is_visit.add((pos_x, pos_y))
                        coord_path = current_path + [direction]
                        stack.append(((pos_x, pos_y), coord_path))

        return []

    def solve(self, maze, screen=None):
        from mazegen import MazeGenerator
        height = len(maze)
        width = len(maze[0])
        maze[self.start[0]][self.start[1]] = 6
        x, y = self.end
        if x >= height or y >= width:
            raise ValueError("Invalid end coordinate")
        if (
            maze[self.end[0]][self.end[1]] != 1
            and maze[self.end[0]][self.end[1]] != 7
        ):
            raise ValueError("Invalid end coordinate")
        if self.start == self.end:
            return maze
        maze[x][y] = 7
        path_dfs = self.find_path_dfs(maze, screen)
        x, y = self.start
        moove_matrix = {"N": (-1, 0),
                        "S": (1, 0),
                        "W": (0, -1),
                        "E": (0, 1)}
        for coord in path_dfs:
            if maze[x][y] == 4:
                maze[x][y] = 3
            d_x, d_y = moove_matrix[coord]
            x += d_x
            y += d_y
            if maze[x][y] == 4:
                maze[x][y] = 3
            MazeGenerator.print_maze(screen, maze)
            time.sleep(1/60)
            screen.refresh()
        return path_dfs
