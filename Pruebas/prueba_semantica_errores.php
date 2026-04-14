<?php
// ERROR 1: Asignar a un índice de un arreglo que no existe
$arreglo_fantasma[0] = 100;

// ERROR 2: Intentar usar count() en una variable que no existe
$tamano = count($variable_inexistente);

// ERROR 3: Usar count() en una variable normal (no arreglo)
$texto = 50;
$falso_tamano = count($texto);

// ERROR 4: Sumar usando una variable no inicializada
$resultado = $texto + $fantasma;

// ERROR 5: Incrementar una variable que nunca nació
$contador_magico++;
?>