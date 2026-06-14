import matplotlib.pyplot as plt

# Inicjalizacja list na dane
x_data = []
y_data = []

# Odczyt danych z pliku etot.dat
with open('data.fit', 'r') as file:
    for line in file:
        # Pomijanie pustych linii
        if not line.strip():
            continue
        # Podział linii na kolumny
        parts = line.split()
        if len(parts) >= 2:
            x_data.append(float(parts[0]))
            y_data.append(float(parts[1]))

# Tworzenie wykresu
plt.figure(figsize=(8, 6))
plt.plot(x_data, y_data, marker='o', linestyle='-', color='b', label='Energia całkowita')

# Dodawanie etykiet i tytułu
plt.title('Wykres zależności energii całkowitej', fontsize=14)
plt.xlabel('Parametr sieci / Odległość (X)', fontsize=12)
plt.ylabel('Energia całkowita (Y)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# Zapisywanie wykresu do pliku JPG
plt.savefig('wykres_energii.jpg', format='jpg', dpi=300)
print("Wykres został pomyślnie zapisany jako 'wykres_energii.jpg'")
