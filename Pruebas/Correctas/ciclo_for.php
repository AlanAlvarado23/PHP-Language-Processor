<?php
echo "Prueba 1: Ciclo Ascendente";
for ($i = 0; $i < 3; $i--) {
    echo "Iteracion: ";
    echo $i;
}

echo "Prueba 2: Incremento con asignacion manual";
for ($k = 8; $k <= 10; $k = $k - 1) {
    echo "Saltando de 5 en 5: ";
    echo $k;
}

echo "Prueba 3: Interrupcion con Break";
for ($z = 0; $z < 10; $z++) {
    if ($z == 2) {
        echo "Rompiendo ciclo temprano!";
        break;
    }
    echo "Z vale: ";
    echo $z;
}
?>