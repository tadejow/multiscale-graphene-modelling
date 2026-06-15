"""
Module responsible for generating the 2D computational domain and FEM mesh.
Recreates the ETHZ experimental geometry using Gmsh and imports it to dolfinx.
"""
import logging
import gmsh
from mpi4py import MPI
from dolfinx.io import gmshio
from dolfinx.mesh import Mesh

class GrapheneDeviceMesh:
    def __init__(self, length: float, width: float, radius: float, cx: float, cy: float, resolution: int):
        self.length = length
        self.width = width
        self.radius = radius
        self.cx = cx
        self.cy = cy
        self.resolution = resolution
        self.mesh = self._build_mesh()

    def _build_mesh(self) -> Mesh:
        logging.info("Initializing Gmsh and constructing solid geometry (CSG)...")
        gmsh.initialize()
        gmsh.model.add("graphene_device")

        # 1. Główny kanał
        rect = gmsh.model.occ.addRectangle(-self.length / 2.0, 0.0, 0.0, self.length, self.width)

        # 2. Dysk (kieszeń hydrodynamiczna)
        disk = gmsh.model.occ.addDisk(self.cx, self.cy, 0.0, self.radius, self.radius)

        # 3. Operacja Boole'a - Unia geometrii
        gmsh.model.occ.fuse([(2, rect)], [(2, disk)])
        gmsh.model.occ.synchronize()

        # Dodanie grupy fizycznej dla powierzchni (niezbędne do importu FEniCSx)
        gmsh.model.addPhysicalGroup(2, [1], 1)

        # 4. Ustawienie gęstości siatki
        mesh_size = self.length / self.resolution
        gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size)
        gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)

        logging.info(f"Generating FEM mesh with target size {mesh_size}...")
        gmsh.model.mesh.generate(2)

        # 5. Konwersja modelu Gmsh do FEniCSx Mesh
        mesh, cell_markers, facet_markers = gmshio.model_to_mesh(
            gmsh.model, MPI.COMM_WORLD, 0, gdim=2
        )

        gmsh.finalize()
        logging.info("Mesh generated successfully and imported to dolfinx.")

        return mesh

    def get_mesh(self) -> Mesh:
        return self.mesh