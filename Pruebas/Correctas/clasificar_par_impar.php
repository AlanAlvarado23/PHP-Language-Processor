<?php
$i = 1;
$max = 10;

while ($i <= $max) {
    if ($i % 2 == 0) {
        echo "Par: ";
        echo $i;
    } else {
        echo "Impar: ";
        echo $i;
    }
    $i++;
}
?>