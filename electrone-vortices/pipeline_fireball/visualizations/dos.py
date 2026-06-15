import os
import numpy as np
import matplotlib.pyplot as plt


def plot_academic_graphene_dos(filename='../../data/data_fireball/generated_results/dens_TOT.dat'):
    """Plots academic-grade Density of States (DOS) for Graphene with full and zoomed views."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    try:
        data = np.loadtxt(filename)
    except Exception as err:
        print(f"Error loading {filename}: {err}")
        return

    energy = data[:, 0]
    dos = data[:, 1]

    # Locate Dirac point (minimum DOS within the middle 50% range)
    n_points = len(energy)
    mid_start = n_points // 4
    mid_end = 3 * n_points // 4
    dirac_idx = mid_start + np.argmin(dos[mid_start:mid_end])
    e_dirac = energy[dirac_idx]

    # Align Dirac point to 0.0 eV
    energy_shifted = energy - e_dirac

    # Initialize figure with 1 row and 2 columns
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # ==========================================
    # Subplot 1: Full Range (Left)
    # ==========================================
    ax1.plot(energy_shifted, dos, color='#B23B3B', linewidth=1.5)

    # Dynamic X-axis boundary detection for full range
    nonzero_indices = np.where(dos > 1e-4)[0]
    if len(nonzero_indices) > 0:
        xmin = energy_shifted[nonzero_indices[0]] - 0.2
        xmax = energy_shifted[nonzero_indices[-1]] + 0.2
        ax1.set_xlim([xmin, xmax])
    else:
        ax1.set_xlim([-10.0, 10.0])

    ax1.set_ylim(bottom=0.0, top=np.max(dos) * 1.1)
    ax1.set_title('Full Energy Range', fontsize=14, pad=10)

    # ==========================================
    # Subplot 2: Zoomed Range [-3.5 eV, 3.5 eV] (Right)
    # ==========================================
    ax2.plot(energy_shifted, dos, color='#B23B3B', linewidth=1.5)
    ax2.set_xlim([-3.5, 3.5])

    # Find max DOS inside the [-3.5, 3.5] window to scale Y-axis properly
    mask = (energy_shifted >= -3.5) & (energy_shifted <= 3.5)
    if np.any(mask):
        ax2.set_ylim(bottom=0.0, top=np.max(dos[mask]) * 1.1)
    else:
        ax2.set_ylim(bottom=0.0, top=np.max(dos) * 1.1)

    ax2.set_title('Zoomed Range $[-3.5\ \mathrm{eV}, 3.5\ \mathrm{eV}]$', fontsize=14, pad=10)

    # ==========================================
    # Academic styling applied to both subplots
    # ==========================================
    for ax in [ax1, ax2]:
        ax.tick_params(direction='in', top=True, right=True, which='both', labelsize=12, width=1.0)
        ax.set_xlabel('E', fontsize=14, family='sans-serif', style='italic')
        ax.set_ylabel('D(E)', fontsize=14, family='sans-serif', style='italic')

        # Frame adjustment
        for spine in ['top', 'bottom', 'left', 'right']:
            ax.spines[spine].set_color('black')
            ax.spines[spine].set_linewidth(1.0)

    plt.tight_layout()

    # Save the figure
    output_image = '../../data/data_fireball/visualizations/graphene_dos_academic.png'
    os.makedirs(os.path.dirname(output_image), exist_ok=True)  # Zabezpieczenie przed brakiem folderu
    plt.savefig(output_image, dpi=400)
    print(f"Plot successfully generated and saved as: {output_image}")
    plt.show()


if __name__ == '__main__':
    plot_academic_graphene_dos()