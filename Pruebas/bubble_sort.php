<?php

$datos = array(64, 34, 25, 12, 22, 11, 90);
$n = count($datos);

// Algoritmo Bubble Sort lineal (sin funciones externas)
for ($i = 0; $i < $n; $i++) {
    for ($j = 0; $j < $n - $i - 1; $j++) {
        
        if ($datos[$j] > $datos[$j + 1]) {
            // Swap (intercambio)
            $temporal = $datos[$j];
            $datos[$j] = $datos[$j + 1];
            $datos[$j + 1] = $temporal;
        }
    }
}

// Imprimir los resultados usando un bucle que tu compilador entiende
for ($k = 0; $k < $n; $k++) {
    echo $datos[$k];
}

?>