from mazegen import MazeGenerator
from pydantic import ValidationError
from dfs_path import DFS
import sys


def output_maze(lines: list[str], start: tuple[int, int],
                end: tuple[int, int], path_find: str) -> None:
    with open("output_maze.txt", 'w') as file:
        for line in lines:
            file.write(line + '\n')
        file.write('\n')
        file.write(f"{start[0]},{start[1]}\n")
        file.write(f"{end[0]},{end[1]}\n")
        file.write("".join(path_find) + '\n')


def parse_config(filename: str) -> dict[str, str]:
    read_file = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=', 1)
            read_file[key] = value
        return read_file


def main() -> None:
    av = sys.argv
    ac = len(av)
    if ac != 2:
        print('error arg')
        sys.exit(1)
    try:
        generator = MazeGenerator(height=20, width=20)
        config = parse_config(av[1])
        maze = generator.maze_gen()
        start_pos = tuple(map(int, config['ENTRY'].split(',')))
        end_pos = tuple(map(int, config['EXIT'].split(',')))
        solver_dfs = DFS()
        path_find = solver_dfs.find_path_dfs(start_pos, end_pos, maze)
        hex_map = generator.convert_hex_maze(maze)
        output_maze(hex_map, start_pos, end_pos, path_find)
    except ValidationError as e:
        for error in e.errors():
            print(error['msg'])


main()
