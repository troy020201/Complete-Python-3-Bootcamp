"""
Simple 3D terrain builder for Dungeons & Dragons.

This module provides a minimal set of utilities to generate grid based
dungeon terrain and export it as an ASCII STL file for 3D printing.

The implementation is intentionally lightweight and does not rely on
external libraries. It supports creation of floor tiles and walls
represented by boxes composed of triangles.
"""

from dataclasses import dataclass
from typing import List, Tuple

Vector = Tuple[float, float, float]


def _facet(normal: Vector, v1: Vector, v2: Vector, v3: Vector) -> str:
    """Return an STL facet string for the given normal and vertices."""
    facet = [
        f"  facet normal {normal[0]} {normal[1]} {normal[2]}",
        "    outer loop",
        f"      vertex {v1[0]} {v1[1]} {v1[2]}",
        f"      vertex {v2[0]} {v2[1]} {v2[2]}",
        f"      vertex {v3[0]} {v3[1]} {v3[2]}",
        "    endloop",
        "  endfacet",
    ]
    return "\n".join(facet)


@dataclass
class Mesh:
    """Container for STL triangles."""
    triangles: List[str]

    def __init__(self) -> None:
        self.triangles = []

    def add_box(self, origin: Vector, size: Vector) -> None:
        """Add triangles representing a box."""
        x, y, z = origin
        w, d, h = size
        # 8 vertices of the box
        p = [
            (x, y, z),  # 0
            (x + w, y, z),  # 1
            (x + w, y + d, z),  # 2
            (x, y + d, z),  # 3
            (x, y, z + h),  # 4
            (x + w, y, z + h),  # 5
            (x + w, y + d, z + h),  # 6
            (x, y + d, z + h),  # 7
        ]
        # each face normal and vertices (two triangles per face)
        faces = [
            ((0, 0, -1), (0, 0, 1, 2)),  # bottom
            ((0, 0, 1), (4, 5, 6, 7)),  # top
            ((0, -1, 0), (0, 1, 5, 4)),  # front
            ((1, 0, 0), (1, 2, 6, 5)),  # right
            ((0, 1, 0), (2, 3, 7, 6)),  # back
            ((-1, 0, 0), (3, 0, 4, 7)),  # left
        ]
        for normal, (a, b, c, d) in faces:
            self.triangles.append(_facet(normal, p[a], p[b], p[c]))
            self.triangles.append(_facet(normal, p[a], p[c], p[d]))

    def write_ascii_stl(self, filename: str, solid_name: str = "terrain") -> None:
        """Write triangles to an ASCII STL file."""
        with open(filename, "w") as f:
            f.write(f"solid {solid_name}\n")
            for tri in self.triangles:
                f.write(tri + "\n")
            f.write(f"endsolid {solid_name}\n")


class TerrainBuilder:
    """Builds a simple grid based dungeon terrain."""

    def __init__(
        self,
        tile_size: float = 1.0,
        tile_height: float = 0.2,
        wall_height: float = 1.0,
        wall_thickness: float = 0.1,
    ) -> None:
        self.tile_size = tile_size
        self.tile_height = tile_height
        self.wall_height = wall_height
        self.wall_thickness = wall_thickness
        self.mesh = Mesh()

    def add_floor(self, width: int, depth: int) -> None:
        """Add a floor grid of the given number of tiles."""
        for i in range(width):
            for j in range(depth):
                origin = (i * self.tile_size, j * self.tile_size, 0)
                size = (self.tile_size, self.tile_size, self.tile_height)
                self.mesh.add_box(origin, size)

    def add_wall(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Add a wall segment from start to end tile coordinates."""
        sx, sy = start
        ex, ey = end
        dx = ex - sx
        dy = ey - sy
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            return
        # normalized direction
        nx, ny = dx / length, dy / length
        # wall origin at start tile
        ox = sx * self.tile_size
        oy = sy * self.tile_size
        origin = (
            ox + (self.tile_size - self.wall_thickness) / 2 * (1 - abs(ny)),
            oy + (self.tile_size - self.wall_thickness) / 2 * (1 - abs(nx)),
            self.tile_height,
        )
        size = (
            self.wall_thickness if nx != 0 else self.tile_size * length,
            self.wall_thickness if ny != 0 else self.tile_size * length,
            self.wall_height,
        )
        self.mesh.add_box(origin, size)

    def export(self, filename: str) -> None:
        """Export the terrain to an STL file."""
        self.mesh.write_ascii_stl(filename)


if __name__ == "__main__":
    builder = TerrainBuilder()
    builder.add_floor(3, 3)
    builder.add_wall((0, 0), (3, 0))
    builder.add_wall((3, 0), (3, 3))
    builder.add_wall((3, 3), (0, 3))
    builder.add_wall((0, 3), (0, 0))
    builder.export("terrain.stl")
