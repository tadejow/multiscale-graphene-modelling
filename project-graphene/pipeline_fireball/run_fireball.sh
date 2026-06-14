#!/bin/bash

# ==============================================================================
# POBIERAMY PEŁNĄ ŚCIEŻKĘ DO OBECNEGO KATALOGU (GRAPHENE)
# ==============================================================================
BASE_DIR=$(pwd)

# Ścieżka do programu fireball.x
FIREBALL_EXEC="$BASE_DIR/fireball.x"

# Ścieżka do bazy danych z parametrami atomów
FDATA_PATH="/home/em0/Fdata_H-ss_C-spd_Si-spd"

# Nadajemy uprawnienia
chmod +x $FIREBALL_EXEC

# Zakres deformacji (rozciąganie/ściskanie sieci)
alat=$(LC_NUMERIC=C seq -s ' ' 2.0 0.001 3.0)

# Główne ścieżki
RESULTS_DIR="../RESULTS"

# Tworzymy główny katalog RESULTS
mkdir -p $RESULTS_DIR

# Plik CSV do którego zbierzemy dane
echo "Lattice,E_tot,E_fermi" > $RESULTS_DIR/summary.csv

for i in $alat; do
    echo "======================================"
    echo "Rozpoczynam obliczenia dla sieci: $i"
    
    # Tworzymy folder roboczy
    WORK_DIR="$RESULTS_DIR/$i"
    mkdir -p $WORK_DIR
    
    # Kopiujemy oryginalne pliki
    cp C1.bas C1.lvs C1.32.kpts dos.optional $WORK_DIR/
    
    # Tworzymy fireball.in podmieniając AAA na aktualną stałą sieci
    sed "s/AAA/$i/g" fireball.sample > $WORK_DIR/fireball.in
    
    # Tworzymy plik kierujący do bazy danych
    echo "$FDATA_PATH" > $WORK_DIR/Fdata.optional
    
    # Wchodzimy do folderu roboczego
    cd $WORK_DIR
    
    # Uruchamiamy Fireball
    $FIREBALL_EXEC > out_$i.log
    
    # ================= WYCIĄGANIE DANYCH =================
    ETOT=$(grep "etot/atom" out_$i.log | cut -b50-65 | xargs)
    EFERMI=$(grep "Fermi" out_$i.log | tail -n 1 | awk '{print $NF}')
    
    # Zapis do CSV
    echo "$i,$ETOT,$EFERMI" >> ../summary.csv
    
    # Wyciągamy pliki kluczowe dla uczenia maszynowego
    if [ -f "eigen.dat" ]; then
        cp eigen.dat ../eigen_$i.dat
    fi
    
    if [ -f "dens_TOT.dat" ]; then
        cp dens_TOT.dat ../dens_$i.dat
    fi
    
    echo "Zakończono: E_tot = $ETOT | E_F = $EFERMI"
    
    # Wracamy do głównego folderu
    cd $BASE_DIR
done

echo "======================================"
echo "Wszystkie obliczenia zakończone!"
echo "Pakuję wyniki do pobrania..."

# Wychodzimy, żeby spakować RESULTS
cd ..
tar czvf RESULTS.tgz RESULTS/

echo "Gotowe! Sprawdź folder PROJEKT. Używając WinSCP pobierz plik RESULTS.tgz"
