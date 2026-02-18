from mazegen import MazeGenerator
import curses as cs
from pydantic import ValidationError
import sys


def output_maze(lines: list[str], start: MazeGenerator) -> None:
    with open("output_maze.txt", 'w') as file:
        for line in lines:
            file.write(line + '\n')
        file.write('\n')
        file.write(f"{start[0]},{start[1]}")
        # file.write(f"{end[0]}, {end[1]}")


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
        config = parse_config(av[1])
        generator = MazeGenerator(height=20, width=20)
        start = generator.start
        end = generator.end
        maze = generator.maze_gen()
        hex_maze = generator.convert_hex_maze(maze)
        output_maze(hex_maze, start, end)
    except ValidationError as e:
        for error in e.errors():
            print(error['msg'])


main()
