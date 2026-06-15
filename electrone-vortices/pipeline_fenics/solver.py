"""
Module formulating and solving the Gurzhi (electronic Navier-Stokes) equation in dolfinx.
Utilizes Mixed Finite Elements (Taylor-Hood P2-P1) for the saddle-point problem.
"""
import logging
import numpy as np
import ufl
import basix.ufl
from dolfinx import fem, mesh
from dolfinx.fem.petsc import LinearProblem
from petsc4py import PETSc
from mpi4py import MPI

class GurzhiSolver:
    def __init__(self, domain: mesh.Mesh, D_nu: float, inflow_J: float, L: float, W: float):
        self.mesh = domain
        self.D_nu = D_nu
        self.inflow_J = inflow_J
        self.L = L
        self.W = W

        # Setup przestrzeni funkcyjnych
        self.W_space = self._create_function_space()
        self.bcs = self._define_boundary_conditions()

    def _create_function_space(self) -> fem.FunctionSpace:
        logging.info("Setting up Taylor-Hood (P2-P1) mixed function spaces...")
        # Elementy Taylor-Hood dla stabilności LBB
        cell_name = self.mesh.topology.cell_name()
        V_element = basix.ufl.element("CG", cell_name, 2, shape=(self.mesh.geometry.dim,)) # Prędkość
        P_element = basix.ufl.element("CG", cell_name, 1) # Potencjał zrelaksowany (ciśnienie)

        mixed_element = basix.ufl.mixed_element([V_element, P_element])
        return fem.functionspace(self.mesh, mixed_element)

    def _define_boundary_conditions(self):
        fdim = self.mesh.topology.dim - 1 # Wymiar brzegu (1D dla 2D domeny)

        # Identyfikacja poszczególnych brzegów
        def inlet_marker(x): return np.isclose(x[0], -self.L / 2.0)
        def outlet_marker(x): return np.isclose(x[0], self.L / 2.0)
        def wall_marker(x): return ~(np.isclose(x[0], -self.L / 2.0) | np.isclose(x[0], self.L / 2.0))

        # Ekstrakcja zdegenerowanych podprzestrzeni (sub-spaces)
        V, _ = self.W_space.sub(0).collapse() # Podprzestrzeń wektorowa J
        Q, _ = self.W_space.sub(1).collapse() # Podprzestrzeń skalarna phi

        # 1. Warunek brzegowy - Wejście (Inlet J)
        inflow_velocity = fem.Function(V)
        inflow_velocity.interpolate(lambda x: np.vstack((np.full(x.shape[1], self.inflow_J), np.zeros(x.shape[1]))))
        inlet_facets = mesh.locate_entities_boundary(self.mesh, fdim, inlet_marker)
        inlet_dofs = fem.locate_dofs_topological((self.W_space.sub(0), V), fdim, inlet_facets)
        bc_in = fem.dirichletbc(inflow_velocity, inlet_dofs, self.W_space.sub(0))

        # 2. Warunek brzegowy - Ściany (No-slip, J = 0)
        zero_velocity = fem.Function(V)
        zero_velocity.x.array[:] = 0.0
        wall_facets = mesh.locate_entities_boundary(self.mesh, fdim, wall_marker)
        wall_dofs = fem.locate_dofs_topological((self.W_space.sub(0), V), fdim, wall_facets)
        bc_wall = fem.dirichletbc(zero_velocity, wall_dofs, self.W_space.sub(0))

        # 3. Warunek brzegowy - Wyjście (Uziemienie, phi = 0)
        zero_pressure = fem.Function(Q)
        zero_pressure.x.array[:] = 0.0
        outlet_facets = mesh.locate_entities_boundary(self.mesh, fdim, outlet_marker)
        outlet_dofs = fem.locate_dofs_topological((self.W_space.sub(1), Q), fdim, outlet_facets)
        bc_out = fem.dirichletbc(zero_pressure, outlet_dofs, self.W_space.sub(1))

        return [bc_in, bc_wall, bc_out]

    def solve(self):
        logging.info("Formulating the Weak Form of the Gurzhi Equation...")

        # Funkcje próbne (Trial) i testowe (Test)
        u, p = ufl.TrialFunctions(self.W_space)
        v, q = ufl.TestFunctions(self.W_space)

        # Sformułowanie słabe (Wariacyjne)
        a = (
            ufl.inner(u, v) * ufl.dx
            + (self.D_nu ** 2) * ufl.inner(ufl.grad(u), ufl.grad(v)) * ufl.dx
            - p * ufl.div(v) * ufl.dx
            - q * ufl.div(u) * ufl.dx
        )

        f = fem.Constant(self.mesh, PETSc.ScalarType((0.0, 0.0)))
        L_form = ufl.inner(f, v) * ufl.dx

        # Konfiguracja Solwera (MUMPS dla stabilności problemu Stokesa)
        logging.info("Solving the sparse linear system using MUMPS...")
        problem = LinearProblem(
            a, L_form, bcs=self.bcs,
            petsc_options={"ksp_type": "preonly", "pc_type": "lu", "pc_factor_mat_solver_type": "mumps"}
        )

        w = problem.solve()

        # Ekstrakcja składowych rozwiązania
        J_res = w.sub(0).collapse()
        phi_res = w.sub(1).collapse()

        return J_res, phi_res