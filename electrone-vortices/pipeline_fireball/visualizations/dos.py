import os
import numpy as np
import matplotlib.pyplot as plt


def plot_academic_graphene_dos(filename='../../data/data_fireball/generated_results/dens_TOT.dat'):
    """Plots academic-grade Density of States (DOS) for Graphene."""
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

    # Initialize figure
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.plot(energy_shifted, dos, color='#B23B3B', linewidth=1.5)

    # Academic styling configurations
    ax.tick_params(direction='in', top=True, right=True, which='both', labelsize=12, width=1.0)
    ax.set_xlabel('E', fontsize=14, family='sans-serif', style='italic')
    ax.set_ylabel('D(E)', fontsize=14, family='sans-serif', style='italic')

    # Dynamic X-axis boundary detection
    nonzero_indices = np.where(dos > 1e-4)[0]
    if len(nonzero_indices) > 0:
        xmin = energy_shifted[nonzero_indices[0]] - 0.2
        xmax = energy_shifted[nonzero_indices[-1]] + 0.2
        ax.set_xlim([xmin, xmax])
    else:
        ax.set_xlim([-10.0, 10.0])

    ax.set_ylim(bottom=0.0, top=np.max(dos) * 1.1)

    # Frame adjustment
    for spine in ['top', 'bottom', 'left', 'right']:
        ax.spines[spine].set_color('black')
        ax.spines[spine].set_linewidth(1.0)

    plt.tight_layout()
    output_image = '../../data/data_fireball/visualizations/graphene_dos_academic.png'
    plt.savefig(output_image, dpi=400)
    print(f"Plot successfully generated and saved as: {output_image}")
    plt.show()


if __name__ == '__main__':
    plot_academic_graphene_dos()
