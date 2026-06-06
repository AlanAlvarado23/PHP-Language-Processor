<?php
$numeros = array(10, 20, 30, 40, 50);
$total = 0;
$i = 0;
$tam = count($numeros);

while ($i < $tam) {
    $total = $total + $numeros[$i];
    $i++;
}

echo "El total es: ";
echo $total;
?>