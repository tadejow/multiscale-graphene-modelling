echo "--- WYKRES ENERGII (Ostatnie cyfry eV) ---"
echo "----------------------------------------"
while read -r krok energia; do
    if [ -n "$krok" ] && [ -n "$energia" ]; then
        # Wyciągamy cyfry po kropce, żeby zobaczyć małe zmiany
        ułamek=$(echo "$energia" | cut -d'.' -f2 | cut -c1-4)
        
        # Przeliczamy to na prostą liczbę gwiazdek (skala 1-30)
        gwiazdki=$(( 10 + (ułamek % 25) ))
        
        printf "Krok %3d [%s] | " "$krok" "$energia"
        for ((i=0; i<gwiazdki; i++)); do printf "*"; done
        echo ""
    fi
done < etot.dat
