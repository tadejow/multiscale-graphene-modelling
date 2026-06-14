from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# TUTAJ WPISZ WARTOŚĆ ENERGII FERMIEGO Z SUMMARY.CSV
E_fermi = -4.5  # <--- ZMIEŃ NA WARTOŚĆ Z TWOICH OBLICZEŃ
# ==========================================
FILE_NAME = 'eigen.dat'
# 1. Ręczne wczytywanie pliku (omijanie tekstu)
bands_list = []
with open(f'{FILE_NAME}', 'r') as f:
    lines = f.readlines()

for line in lines[1:]:  # Pomijamy pierwszą linijkę (91 18)
    if "---" in line:
        continue  # Pomijamy linijki z tekstem

    # Rozdzielamy linijkę na liczby i zamieniamy na float
    row = [float(val) for val in line.split()]
    if row:
        bands_list.append(row)

# Konwersja na tablicę NumPy
bands = np.array(bands_list)
print(f"Wczytano tablicę o wymiarach: {bands.shape} (k-punkty, pasma)")

# 2. X-oś to indeksy wektorów k (od 0 do 90)
k_points = np.arange(bands.shape[0])

# 3. Rysowanie
plt.figure(figsize=(8, 6))

# Plotujemy każde z 18 pasm
for i in range(bands.shape[1]):
    plt.plot(k_points, bands[:, i] - E_fermi, color='blue', linewidth=1.5)

# Oznaczenia poziomu Fermiego
plt.axhline(0, color='red', linestyle='--', label='Poziom Fermiego (E_F = 0)')

# Pionowe linie oddzielające punkty wysokiej symetrii
# (Mieliśmy 3 odcinki po 30 punktów = indeksy 0, 30, 60, 90)
plt.axvline(0, color='black', linewidth=1)  # Gamma
plt.axvline(30, color='black', linewidth=1)  # M
plt.axvline(60, color='black', linewidth=1)  # K (TU BĘDZIE STOŻEK DIRACA!)
plt.axvline(90, color='black', linewidth=1)  # Gamma

# Etykiety osi X
plt.xticks([0, 30, 60, 90], [r'$\Gamma$', 'M', 'K', r'$\Gamma$'], fontsize=14)
plt.ylabel(r'Energia - $E_F$ (eV)', fontsize=14)
plt.title('Struktura pasmowa grafenu (Fireball TB-DFT)', fontsize=16)

# Ograniczenie widoku osi Y na obszar wokół poziomu Fermiego
plt.ylim(-15, 15)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

# Zapis do pliku
plt.savefig(f'band_structure_{datetime.today().strftime('%Y-%m-%d')}.png', dpi=300)
print("Wykres zapisano pomyślnie jako: band_structure.png")