import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


def plot_dirac_3d(filename='eigen_3d.dat'):
    # Wczytanie pliku
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Parsowanie nagłówka
    tokens = lines[0].split()
    nkpts = int(tokens[0])
    nbands = int(tokens[1])

    energies = np.zeros((nkpts, nbands))
    k_idx = 0
    line_idx = 1

    while k_idx < nkpts and line_idx < len(lines):
        line = lines[line_idx].strip()
        if "------" in line:
            line_idx += 1
            continue

        band_vals = []
        while len(band_vals) < nbands and line_idx < len(lines):
            parts = lines[line_idx].split()
            if "------" not in parts[0]:
                band_vals.extend([float(x) for x in parts])
            line_idx += 1

        if len(band_vals) == nbands:
            energies[k_idx, :] = band_vals
            k_idx += 1

    # Wymiary siatki (zgodne z generatorem BASH)
    N = 41
    delta = 0.8
    Kx, Ky = 3.62759873, 2.09439510

    # Odtwarzamy siatkę X i Y
    X_range = np.linspace(-delta, delta, N)  # Centrujemy układ w (0,0) jako punkcie K
    Y_range = np.linspace(-delta, delta, N)
    X, Y = np.meshgrid(X_range, Y_range, indexing='ij')

    # Wyznaczamy poziom Fermiego w idealnym punkcie K (indeks środkowy: 20 * 41 + 20 = 840)
    fermi_level = (energies[840, 3] + energies[840, 4]) / 2.0

    # Ekstrakcja pasma walencyjnego (3) i przewodnictwa (4) relatywnie do poziomu Fermiego
    Z_valence = energies[:, 3].reshape(N, N) - fermi_level
    Z_conduction = energies[:, 4].reshape(N, N) - fermi_level

    # RYSOWANIE WYKRESU 3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Rysujemy pasmo przewodnictwa (stożek górny)
    surf_cond = ax.plot_surface(X, Y, Z_conduction, cmap=cm.plasma,
                                linewidth=0, antialiased=True, alpha=0.85)

    # Rysujemy pasmo walencyjne (stożek dolny)
    surf_val = ax.plot_surface(X, Y, Z_valence, cmap=cm.viridis,
                               linewidth=0, antialiased=True, alpha=0.85)

    # Konfiguracja osi
    ax.set_title('3D Dirac Cone in Graphene ($E(k_x, k_y)$)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(r'$k_x - K_x \ (\mathrm{\AA}^{-1})$', fontsize=12)
    ax.set_ylabel(r'$k_y - K_y \ (\mathrm{\AA}^{-1})$', fontsize=12)
    ax.set_zlabel(r'$E - E_F \ (\mathrm{eV})$', fontsize=12)

    # Ustawienie ładnego kąta widzenia
    ax.view_init(elev=15, azim=45)

    # Zakres osi Z, by uwypuklić liniowość stożka
    ax.set_zlim([-4, 4])

    plt.tight_layout()
    plt.savefig('graphene_dirac_cone_3d.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    plot_dirac_3d('eigen_3d.dat')  # Podmień nazwę pliku, jeśli pobrałeś go pod inną nazwą