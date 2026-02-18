from mazegen import MazeGenerator
import curses as cs
from pydantic import ValidationError
import sys


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
    config = parse_config(av[1])
    try:
        generator = MazeGenerator(height=5, width=5)
        maze = generator.maze_gen()
    except ValidationError as e:
        for error in e.errors():
            print(error['msg'])


main()
