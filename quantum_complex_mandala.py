import numpy as np
from pyquil import Program, get_qc
from pyquil.gates import H, MEASURE
from PIL import Image, ImageDraw
import math


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

        # Convert results into decimal values
        entropy = [
            sum((bit << idx) for idx, bit in enumerate(measurement))
            for measurement in results
        ]
        return entropy
    except Exception as e:
        print(f"Error generating quantum entropy: {e}")
        return None


def draw_polygon(draw, center_x, center_y, radius, sides, rotation, color, width):
    """Draws a rotated polygon with an outline width."""
    angle_step = 2 * math.pi / sides
    points = [
        (
            center_x + radius * math.cos(rotation + i * angle_step),
            center_y + radius * math.sin(rotation + i * angle_step),
        )
        for i in range(sides)
    ]

    draw.polygon(points, outline=color, fill=None)
    for i in range(sides):
        draw.line([points[i], points[(i + 1) % sides]], fill=color, width=width)


def draw_star(draw, center_x, center_y, outer_radius, inner_radius, points, rotation, color, width):
    """Draws a star shape using alternating radii."""
    angle_step = math.pi / points  # Star points alternate between outer and inner radii
    star_points = []
    for i in range(2 * points):
        r = outer_radius if i % 2 == 0 else inner_radius
        angle = rotation + i * angle_step
        star_points.append((center_x + r * math.cos(angle), center_y + r * math.sin(angle)))

    draw.polygon(star_points, outline=color, fill=None)
    for i in range(len(star_points)):
        draw.line([star_points[i], star_points[(i + 1) % len(star_points)]], fill=color, width=width)


def create_complex_mandala(entropy_data, size=1024, layers=20):
    """Creates a highly detailed mandala pattern using quantum entropy."""
    image = Image.new("RGB", (size, size), "black")  # Black background
    draw = ImageDraw.Draw(image)

    center_x, center_y = size // 2, size // 2  # Canvas center

    for layer in range(layers):
        radius = (layer + 1) * (size // (2 * layers))

        # Quantum randomness for radial symmetry (spokes)
        radial_symmetry = 8 + entropy_data[layer % len(entropy_data)] % 28  # Between 8 and 36
        sides = 4 + entropy_data[layer % len(entropy_data)] % 9  # Square to Nonagon
        rotation = math.radians(entropy_data[(layer * 2) % len(entropy_data)] % 360)

        # Define line width variations (thicker in outer layers)
        line_width = max(1, (layers - layer) // 3)

        for i in range(radial_symmetry):
            angle = 2 * math.pi * i / radial_symmetry
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Vibrant but slightly muted colors for better visibility
            color = (
                100 + entropy_data[(layer + i) % len(entropy_data)] % 156,  # Red (100-255)
                50 + entropy_data[(layer + i + 1) % len(entropy_data)] % 156,  # Green (50-205)
                100 + entropy_data[(layer + i + 2) % len(entropy_data)] % 156,  # Blue (100-255)
            )

            # Alternate between circles, polygons, and stars
            shape_choice = entropy_data[(layer + i) % len(entropy_data)] % 3
            if shape_choice == 0:
                shape_radius = 8 + (entropy_data[(layer + i) % len(entropy_data)] % 25)
                draw.ellipse(
                    [x - shape_radius, y - shape_radius, x + shape_radius, y + shape_radius],
                    outline=color, width=line_width,
                )
            elif shape_choice == 1:
                polygon_radius = 12 + (entropy_data[(layer + i) % len(entropy_data)] % 30)
                draw_polygon(draw, x, y, polygon_radius, sides, rotation, color, width=line_width)
            else:
                outer_radius = 15 + (entropy_data[(layer + i) % len(entropy_data)] % 35)
                inner_radius = outer_radius * 0.4
                star_points = 5 + entropy_data[(layer + i) % len(entropy_data)] % 6  # 5 to 10 points
                draw_star(draw, x, y, outer_radius, inner_radius, star_points, rotation, color, width=line_width)

    return image


def main():
    num_qubits = 9
    num_shots = 256
    size = 1024

    print("Generating quantum entropy...")
    entropy_data = generate_quantum_entropy(num_qubits, num_shots)

    if entropy_data:
        print(f"Generated {len(entropy_data)} entropy values.")
        print("Creating highly detailed mandala image...")
        mandala_image = create_complex_mandala(entropy_data, size=size, layers=24)

        print("Saving detailed mandala image...")
        mandala_image.save("quantum_complex_mandala.png")
        print("Complex mandala image saved as 'quantum_complex_mandala.png'.")
    else:
        print("Failed to generate quantum entropy.")


if __name__ == "__main__":
    main()
