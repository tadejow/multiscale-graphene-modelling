import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


def plot_dirac_3d(filename='../../data/data_fireball/generated_results/eigen_3d.dat'):
    """Parses 3D eigenvalue data to visualize the Graphene Dirac Cone."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    with open(filename, 'r') as file:
        lines = file.readlines()

    # Parse header info
    header_tokens = lines[0].split()
    nkpts = int(header_tokens[0])
    nbands = int(header_tokens[1])

    energies = np.zeros((nkpts, nbands))
    k_idx = 0
    line_idx = 1

    # Parse eigenvalue blocks
    while k_idx < nkpts and line_idx < len(lines):
        line = lines[line_idx].strip()
        if "------" in line:
            line_idx += 1
            continue

        band_vals = []
        while len(band_vals) < nbands and line_idx < len(lines):
            parts = lines[line_idx].split()
            if parts and "------" not in parts[0]:
                band_vals.extend([float(x) for x in parts])
            line_idx += 1

        if len(band_vals) == nbands:
            energies[k_idx, :] = band_vals
            k_idx += 1

    # Grid reconstruction settings
    grid_size = 41
    delta = 0.8

    x_range = np.linspace(-delta, delta, grid_size)
    y_range = np.linspace(-delta, delta, grid_size)
    grid_x, grid_y = np.meshgrid(x_range, y_range, indexing='ij')

    # Fermi level extraction at the K-point (index 840)
    fermi_level = (energies[840, 3] + energies[840, 4]) / 2.0

    # Reshape bands relative to Fermi level
    z_valence = energies[:, 3].reshape(grid_size, grid_size) - fermi_level
    z_conduction = energies[:, 4].reshape(grid_size, grid_size) - fermi_level

    # 3D Plot Generation
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot upper conduction cone
    ax.plot_surface(grid_x, grid_y, z_conduction, cmap=cm.plasma,
                    linewidth=0, antialiased=True, alpha=0.85)

    # Plot lower valence cone
    ax.plot_surface(grid_x, grid_y, z_valence, cmap=cm.viridis,
                    linewidth=0, antialiased=True, alpha=0.85)

    # Axis properties
    ax.set_title('3D Dirac Cone in Graphene ($E(k_x, k_y)$)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(r'$k_x - K_x \ (\mathrm{\AA}^{-1})$', fontsize=12)
    ax.set_ylabel(r'$k_y - K_y \ (\mathrm{\AA}^{-1})$', fontsize=12)
    ax.set_zlabel(r'$E - E_F \ (\mathrm{eV})$', fontsize=12)

    ax.view_init(elev=15, azim=45)
    ax.set_zlim([-4, 4])

    plt.tight_layout()
    output_image = '../../data/data_fireball/visualizations/graphene_dirac_cone_3d.png'
    plt.savefig(output_image, dpi=300)
    print(f"Plot successfully saved as '{output_image}'")
    plt.show()


if __name__ == '__main__':
    plot_dirac_3d()
