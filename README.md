*This project has been created as part of the 42 curriculum by rdedack, thsykas.*
# A-Maze-ing: Procedural Maze Generation and Visualization


Welcome to the comprehensive technical documentation for **A-Maze-ing**. This project demonstrates advanced applications of graph theory, procedural generation, and strict Python packaging. It is designed to generate perfect (or imperfect) mazes, output them in a specific hexadecimal format, and provide a visual rendering interface.

---

## Table of Contents

1. [System Architecture & Module Overview](#1-system-architecture--module-overview)
2. [File Structure & Component Roles](#2-file-structure--component-roles)
3. [Deep Dive: Core Logic & Algorithms](#3-deep-dive-core-logic--algorithms)
4. [Configuration File Format](#4-configuration-file-format)
5. [Hexadecimal Output Format](#5-hexadecimal-output-format)
6. [Installation & Usage](#6-installation--usage)
7. [Team & Project Management](#7-team--project-management)
8. [Resources & AI Usage](#8-resources--ai-usage)

---
## DESCRIPTION
**A-Maze-ing** is a Python programming project whose objective is to design a maze generator capable of creating complex, random structures that are:

- either **perfect** (a single unique path between the entry and the exit),
- or **imperfect** (multiple possible paths).
The project is not limited to generation: it also includes the implementation of **pathfinding** algorithms in order to resolve the maze by finding the shortest path between the starting point and the exit.

The implemented algorithms are:

- **DFS (Depth-First Search)** for generation and resolution,
- **A\*** (A-Star) for optimized shortest path search.

The educational objective is to understand:
- search optimization
- the manipulation of grids and data structures

## INSTRUCTION
The project contains a **Makefile** with several rules:
- `make` → runs the program
- `make lint` → checks compliance with `flake8` and `mypy`
- `make lint-strict` → executes `flake8` and `mypy` in strict mode (`--strict`)

## 1. System Architecture & Module Overview

The architecture is strictly decoupled into two main environments: the **application entry point** and the **reusable standalone module** (`mazegen-*`).

<details>
<summary><strong>🔍 Architecture Flow Diagram & Reusability</strong></summary>

The system handles data in four distinct layers:

1. **Ingestion:** Parsing and validating `config.txt` to extract `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE`, and `PERFECT` flags.
2. **Generation (`mazegen`):** A standalone, pip-installable module containing the `MazeGenerator` class. It is entirely independent of the CLI.
3. **Solver:** A pathfinding engine to determine the shortest valid path consisting of `N`, `E`, `S`, `W`.
4. **Presentation:**
   * File output via bitwise hexadecimal encoding* Visual output via Terminal ASCII or MLX.

</details>

---

## 2. File Structure & Component Roles

<details>
<summary><strong>📂 Expand to Explore the Repository Structure</strong></summary>

<pre><code>a-maze-ing/
│
├── a_maze_ing.py          # Main executable script ── config.txt             # Default configuration parameters
├── Makefile               # Task automation (install, run, clean, lint) ── pyproject.toml         # Build system configuration for the `mazegen` wheel
│
└── mazegen/               # Reusable Python package ── __init__.py
    ├── generator.py       # Contains the MazeGenerator class
    ├── solver.py          # Pathfinding algorithms (BFS/A*)
    ├── hex_exporter.py    # Logic for hexadecimal file formatting
    └── renderer.py        # ASCII/MLX visualizer logic
</code></pre>

</details>

<details>
<summary><strong>📄 Expand to read: Detailed File Roles</strong></summary>

* **`a_maze_ing.py`**: The main entry point. It manages exception handling to avoid unexpected crashes, parses CLI arguments, and orchestrates the generator and renderer.
* **`mazegen/generator.py`**: Houses the `MazeGenerator` class. It implements the graph theory algorithms required to carve paths, ensuring connectivity and the integration of the mandatory "42" structural pattern.
* **`mazegen/hex_exporter.py`**: Manages the I/O context managers, writing the maze row by row and appending the entry, exit, and solution.
* **`Makefile`**: Exposes rules like `install` (via pip/uv), `run`, `debug`, `clean`, and `lint` (enforcing `flake8` and `mypy` strict type checking).

</details>

---

## 3. Deep Dive: Core Logic & Algorithms

### 3.1 Random Generation Algorithms

<details>
<summary><strong>🧠 Expand to read: Perfect Maze Generation & Graph Theory</strong></summary>

To satisfy the `PERFECT=True` requirement, the generated maze must be a spanning tree, meaning there is exactly one unique path between any two cells and no loops.



* **Chosen Algorithm:** We utilize a Recursive Backtracker (Depth-First Search approach) combined with randomized neighbor selection.
* **Why this algorithm?** It is memory-efficient for typical terminal sizes and naturally creates long, winding corridors ("river" patterns) which are visually appealing and respect the rule forbidding large open areas (no 3x3 open spaces).
* **Execution Flow:**
    1. Initialize a grid of size `WIDTH` x `HEIGHT` where all cells have 4 walls (N, E, S, W) 2. Start at a random cell, mark it as visited.
    3. Randomly select an unvisited neighboring cell. Remove the shared wall between them.
    4. Push the current cell to a stack and move to the neighbor.
    5. If a cell has no unvisited neighbors (a dead end), pop from the stack to backtrack until a valid neighbor is found.
    6. Stop when the stack is empty.

</details>

### 3.2 The Mandatory "42" Pattern

<details>
<summary><strong>Expand to read: Hardcoding the '42' Structure</strong></summary>

The maze must visually represent a "42" drawn by several fully closed cells.

* **Logic:** Before running the Recursive Backtracker, the `MazeGenerator` maps out a bounding box in the center of the grid. Within this box, specific cells are flagged as "immutable blocks".
* **Pathfinding Constraint:** The generation algorithm treats these immutable blocks as bounds (out-of-bounds), guaranteeing they remain fully closed.
* **Edge Case Handling:** If `WIDTH` and `HEIGHT` are too small to accommodate the pattern (e.g., 5x5), the system omits it and gracefully logs an error message to the console without crashing.

</details>

### 3.3 The Shortest Path Solver

<details>
<summary><strong>🗺️ Expand to read: BFS Pathfinding Implementation</strong></summary>

After generating the maze, the system must calculate the shortest valid path from `ENTRY` to `EXIT`.



* **Algorithm:** Breadth-First Search (BFS).
* **Why BFS?** In an unweighted graph (which a grid maze fundamentally is), BFS guarantees the discovery of the absolute shortest path.
* **Data Structure:** A `collections.deque` is used for O(1) pop/append operations. The queue stores tuples containing the current cell coordinates and the accumulated path string (e.g., "SSEE").

</details>

---

## 4. Configuration File Format

The program accepts a strictly formatted `.txt` file<details>
<summary><strong>⚙️ Expand to read: Configuration Specifications</strong></summary>

The configuration file requires `KEY=VALUE` pairs. Lines starting with `#` are ignored19.

<pre><code># Configuration example
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
</code></pre>

* `ENTRY` and `EXIT` must be valid coordinates inside the bounds.
* A default configuration file is provided in the Git repository.

</details>

---

## 5. Hexadecimal Output Format

The output file encoding is highly specific to allow for fast, binary-level validation<details>
<summary><strong>Expand to read: Bitwise Wall Encoding</strong></summary>

Each cell's wall configuration is stored as a 4-bit integer, translated into a single Hexadecimal character.

| Bit | Value | Direction |
|-----|-------|-----------|
| 0 (LSB) | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

* **Logic:** If a wall is closed, the bit is 1.g., a cell with North and West walls closed is 1 + 8 = 9. If East and West are closed, it's 2 + 8 = 10 -> A.
* **File Structure:**
    1. Grid rows represented as contiguous hex strings, one row per line 2. An empty line 3. Entry coordinates 4. Exit coordinates 5. The solution path string (N, E, S, W).

</details>

---

## 6. Installation & Usage

<details>
<summary><strong> Expand for execution and module usage guidelines</strong></summary>

### Running the Application

Ensure you have Python 3.10 or later installed.

**Install dependencies:**
<pre><code>make install</code></pre>

**Run the generator:**
<pre><code>python3 a_maze_ing.py config.txt</code></pre>

**Run Linting (Flake8 & MyPy):**
<pre><code>make lint</code></pre>

### Using the `mazegen` Module in Other Projects

To reuse the logic:
<pre><code>python3 -m build
pip install dist/mazegen-1.0.0-py3-none-any.whl</code></pre>

**Instantiation Example:**
<pre><code>from mazegen.generator import MazeGenerator

# Instantiate with custom parameters 
generator = MazeGenerator(width=20, height=20, perfect=True, seed=42)
maze_structure = generator.generate()

# Access solution
solution = generator.solve(entry=(0,0), exit=(19,19))
print(f"Path: {solution}")
</code></pre>

</details>

---

## 7. Team & Project Management

<details>
<summary><strong>👥 Expand to read: Workflow by rdedack & thsykas</strong></summary>

* **Roles:** * **rdedack:** Core algorithmic generation (Recursive Backtracker), memory management, and `mazegen` packaging.
  * **thsykas:** UI/UX (MLX / Terminal rendering), pathfinding solver, and Makefile automation.
* **Planning:** Initially, development was split horizontally. Integration faced minor bottlenecks regarding the "42" pattern injection, which was resolved by implementing the immutable bounds check.
* **Tools Used:** `pytest` for unit testing the hex converter, `mypy` for static typing, and virtual environments for dependency isolation.

</details>

---

## 8. Resources & AI Usage

<details>
<summary><strong>🤖 Expand to read: References and Ethics</strong></summary>

* **Resources:** Documentation on Spanning Trees, Kruskal's Algorithm, and Python's build module.
* **AI Usage:** Artificial Intelligence was utilized strictly in adherence to the school guidelines. It was used to generate boilerplate docstrings compliant with PEP 257 and to brainstorm edge-case scenarios for unit tests. All core logic, algorithms, and architectural decisions were engineered, thoroughly reviewed, and fully understood by rdedack and thsykas.

</details>