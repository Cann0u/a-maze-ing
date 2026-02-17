from mazegen import MazeGenerator
import curses as cs
from pydantic import ValidationError

def main() -> None:
    try:
        generator = MazeGenerator(height=5, width=5)
        maze = generator.maze_gen()
    except ValidationError as e:
        for error in e.errors():
            print(error['msg'])


main()
