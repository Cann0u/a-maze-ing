from mazegen import MazeGenerator
import curses as cs
from pydantic import ValidationError


def parse_config() -> dict[str, str]:
    read_file = {}
    with open('config.txt', 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=', 1)
            read_file[key] = value
        return read_file


def main() -> None:
    try:
        generator = MazeGenerator(height=5, width=5)
        maze = generator.maze_gen()
    except ValidationError as e:
        for error in e.errors():
            print(error['msg'])


main()
