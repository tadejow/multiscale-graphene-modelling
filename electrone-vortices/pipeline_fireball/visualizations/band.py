import os
import numpy as np
import matplotlib.pyplot as plt


def plot_band_structure(filename='../../data/data_fireball/generated_results/eigen_2d.dat'):
    """Reads Fireball 2D eigenvalue data and plots the electronic band structure in two subplots."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    # =========================================================================
    # ENTER THE FERMI ENERGY VALUE FROM YOUR SUMMARY.CSV HERE
    E_fermi = -4.5  # <--- Change this to the value from your calculations
    # =========================================================================

    # Load data lines
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Parse header info
    header_tokens = lines[0].split()
    nkpts = int(header_tokens[0])
    nbands = int(header_tokens[1])

    energies = np.zeros((nkpts, nbands))
    k_idx = 0
    line_idx = 1

    # Parse eigenvalue blocks (robust parser from your original script)
    while k_idx < nkpts and line_idx < len(lines):
        line = lines[line_idx].strip()
        if not line or "------" in line:
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

    # Plot configuration - 2 subplots side-by-side (1 row, 2 columns)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    k_points = np.arange(nkpts)

    # Define high-symmetry points (Gamma -> M -> K -> Gamma)
    sym_points = [0, 30, 60, 90]
    sym_labels = [r'$\Gamma$', 'M', 'K', r'$\Gamma$']

    # Loop to apply common settings to both subplots
    for ax in [ax1, ax2]:
        # Plot each band with shifted energy (E - E_F)
        for band in range(nbands):
            ax.plot(k_points, energies[:, band] - E_fermi, linestyle='-', color='b', linewidth=1.5)

        # Red dashed line for the Fermi level (now at 0 eV)
        ax.axhline(0, color='r', linestyle='--', linewidth=1.2, label='Fermi Level ($E_F = 0$)')

        # Vertical grid lines for high-symmetry k-points
        for pt in sym_points:
            ax.axvline(pt, color='black', linewidth=1, alpha=0.7)

        # Axes labels and ticks configurations
        ax.set_xticks(sym_points)
        ax.set_xticklabels(sym_labels, fontsize=13)
        ax.set_xlabel('k-path', fontsize=12)
        ax.set_ylabel(r'Energy - $E_F$ (eV)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.4)

    # --- SUBPLOT 1: Full Picture ---
    ax1.set_title('Full Band Structure', fontsize=14)

    # --- SUBPLOT 2: Zoom around Fermi Level ---
    ax2.set_title('Zoom Around Fermi Level', fontsize=14)
    ax2.set_ylim(-15, 15)  # Restrict the Y-axis view to focus on the Dirac cone
    ax2.legend(loc='upper right')

    # Main title for the entire figure
    plt.suptitle('Graphene Band Structure (Fireball TB-DFT)', fontsize=16, fontweight='bold', y=0.98)

    plt.tight_layout()

    # Safe image saving (automatically creates the 'visualizations' folder if missing)
    output_image = '../../data/data_fireball/visualizations/band_structure.jpg'
    os.makedirs(os.path.dirname(output_image), exist_ok=True)

    plt.savefig(output_image, format='jpg', dpi=300)
    print(f"Plot successfully saved as '{output_image}'")
    plt.show()


if __name__ == '__main__':
    plot_band_structure()