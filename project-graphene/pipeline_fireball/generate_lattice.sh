#!/bin/bash

# ==============================================================================
# GENERATOR SIECI GRAFENU (Sieć trójkątna + 2-punktowa baza)
# ==============================================================================

# Stała sieciowa (bazowa)
a=1.0

echo "Generowanie struktury grafenu dla bazowej stałej sieci a = $a"

# ------------------------------------------------------------------------------
# 1. OBLICZENIA MATEMATYCZNE (używamy AWK do precyzji zmiennoprzecinkowej)
# ------------------------------------------------------------------------------
# Pierwiastek z 3
SQRT3=$(awk 'BEGIN {printf "%.8f", sqrt(3)}')

# Wektory sieci trójkątnej (a1 i a2)
# a1 = a * ( sqrt(3)/2,  0.5 )
# a2 = a * ( sqrt(3)/2, -0.5 )
A1_X=$(awk -v a=$a -v sq3=$SQRT3 'BEGIN {printf "%.8f", a * sq3 / 2}')
A1_Y=$(awk -v a=$a 'BEGIN {printf "%.8f", a * 0.5}')

A2_X=$A1_X
A2_Y=$(awk -v a=$a 'BEGIN {printf "%.8f", a * -0.5}')

# Odległość między najbliższymi sąsiadami w bazie (węgiel-węgiel)
# d_cc = a / sqrt(3)
D_CC=$(awk -v a=$a -v sq3=$SQRT3 'BEGIN {printf "%.8f", a / sq3}')

# ------------------------------------------------------------------------------
# 2. GENEROWANIE PLIKU C1.lvs (Lattice Vectors)
# ------------------------------------------------------------------------------
echo "Tworzenie C1.lvs..."
cat <<EOF > C1.lvs
$A1_X  $A1_Y  0.00000000
$A2_X $A2_Y  0.00000000
0.00000000  0.00000000 60.00000000
EOF

# ------------------------------------------------------------------------------
# 3. GENEROWANIE PLIKU C1.bas (Basis - współrzędne atomów)
# ------------------------------------------------------------------------------
# 6 oznacza liczbę atomową Węgla (C)
# Pierwszy atom w (0,0,0), drugi przesunięty o d_cc w osi X
echo "Tworzenie C1.bas..."
cat <<EOF > C1.bas
      2
6  0.00000000  0.00000000  0.00000000
6  $D_CC  0.00000000  0.00000000
EOF

echo "======================================"
echo "Gotowe! Wygenerowano pliki:"
echo "- C1.lvs (Wektory sieci Bravais'go)"
echo "- C1.bas (Dwupunktowa baza atomów C)"
