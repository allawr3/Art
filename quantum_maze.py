import numpy as np
from pyquil import Program, get_qc
from pyquil.gates import H, MEASURE
from PIL import Image, ImageDraw
import random


def generate_quantum_entropy(num_qubits, num_shots):
    """Generates entropy from quantum measurements."""
    program = Program()
    ro = program.declare('ro', 'BIT', num_qubits)

    # Apply Hadamard gates to all qubits
    for qubit in range(num_qubits):
        program += H(qubit)

    # Add measurement operations
    for qubit in range(num_qubits):
        program += MEASURE(qubit, ro[qubit])

    try:
        qvm = get_qc(f"{num_qubits}q-square-qvm")
        executable = qvm.compile(program)
        results = qvm.run(executable).readout_data['ro']

        # Combine results into decimal values
        entropy = [
            sum((bit << idx) for idx, bit in enumerate(measurement))
            for measurement in results
        ]
        return entropy
    except Exception as e:
        print(f"Error generating quantum entropy: {e}")
        return None


def initialize_maze(size):
    """Initializes a grid maze with all walls."""
    maze = np.ones((size, size), dtype=np.int8)  # 1 = wall, 0 = path
    return maze


def generate_maze(maze, entropy):
    """Generates a maze using quantum randomness."""
    size = maze.shape[0]
    stack = []
    visited = set()

    # Start in the top-left corner
    start_x, start_y = 1, 1
    maze[start_y, start_x] = 0  # Open the starting cell
    visited.add((start_x, start_y))
    stack.append((start_x, start_y))

    directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]  # Up, Down, Left, Right

    while stack:
        current_x, current_y = stack[-1]
        random.shuffle(directions)  # Shuffle the directions for randomness

        moved = False
        for dx, dy in directions:
            nx, ny = current_x + dx, current_y + dy
            if 1 <= nx < size - 1 and 1 <= ny < size - 1 and (nx, ny) not in visited:
                # Open the wall between the current cell and the neighbor
                wall_x, wall_y = current_x + dx // 2, current_y + dy // 2
                maze[wall_y, wall_x] = 0  # Break the wall
                maze[ny, nx] = 0  # Open the neighbor cell
                visited.add((nx, ny))
                stack.append((nx, ny))
                moved = True
                break

        if not moved:
            stack.pop()  # Backtrack if no valid moves

    # Use quantum randomness to introduce additional paths
    for i in range(len(entropy)):
        rand_x = entropy[i % len(entropy)] % (size - 2) + 1
        rand_y = entropy[(i + 1) % len(entropy)] % (size - 2) + 1
        maze[rand_y, rand_x] = 0  # Open random walls

    return maze


def create_maze_image(maze, cell_size=10):
    """Converts the maze into an image."""
    size = maze.shape[0]
    img_size = size * cell_size
    image = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(image)

    # Draw the maze
    for y in range(size):
        for x in range(size):
            if maze[y, x] == 1:  # Wall
                draw.rectangle(
                    [
                        (x * cell_size, y * cell_size),
                        ((x + 1) * cell_size - 1, (y + 1) * cell_size - 1),
                    ],
                    fill="black",
                )

    return image


def main():
    size = 101  # Maze size (must be odd for proper walls)
    num_qubits = 9
    num_shots = size * size
    cell_size = 10  # Size of each cell in pixels

    print("Generating quantum entropy...")
    entropy_data = generate_quantum_entropy(num_qubits, num_shots)

    if entropy_data:
        print(f"Generated {len(entropy_data)} entropy values.")
        print("Initializing maze...")
        maze = initialize_maze(size)

        print("Generating quantum maze...")
        quantum_maze = generate_maze(maze, entropy_data)

        print("Creating maze image...")
        maze_image = create_maze_image(quantum_maze, cell_size=cell_size)

        print("Saving maze image...")
        maze_image.save("quantum_maze.png")
        print("Quantum maze saved as 'quantum_maze.png'.")
    else:
        print("Failed to generate quantum entropy.")


if __name__ == "__main__":
    main()
