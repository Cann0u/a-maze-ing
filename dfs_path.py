class DFS:
    def find_path_dfs(self, start, end, maze_matrix) -> bool:
        stack = [(start, [])]
        is_visit = {start}
        moove_matrix = {(-1, 0): "N",
                        (1, 0): "S",
                        (0, -1): "W",
                        (0, 1): "E"}
        while stack:
            currend_node, current_path = stack.pop()
            if currend_node == end:
                return current_path
            for (m_x, m_y), direction in moove_matrix.items():
                pos_x = currend_node[0] + m_x
                pos_y = currend_node[1] + m_y
                if (
                    0 <= pos_x < len(maze_matrix)
                    and 0 <= pos_y < len(maze_matrix[0])
                    and maze_matrix[pos_x][pos_y] == "⬜"
                ):
                    if (pos_x, pos_y) not in is_visit:
                        is_visit.add((pos_x, pos_y))
                        coord_path = current_path + [direction]
                        stack.append(((pos_x, pos_y), coord_path))
        return []

    def solve(self, maze, start, end):
        path_dfs = self.find_path_dfs(start, end, maze)
        return path_dfs
