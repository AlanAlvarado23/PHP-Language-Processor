<?php
// 1. Inicializamos un arreglo válido
$numeros = array(10, 20, 30, 40, 50);

// 2. Usamos count() en un arreglo real
$limite = count($numeros);

// 3. Inicializamos nuestra variable acumuladora
$suma = 0;

// 4. Ciclo for con inicialización, condición e incremento válidos
for ($i = 0; $i < $limite; $i++) {
    // Leemos el índice del arreglo y reasignamos
    $suma = $suma + $numeros[$i];
}

// 5. Imprimimos el resultado final
echo $suma;
?>