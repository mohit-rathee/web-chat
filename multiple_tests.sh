for ((i=1; i<=100; i++)); do
    python compound_sqlCommands.py
    echo $i
    wait
done
