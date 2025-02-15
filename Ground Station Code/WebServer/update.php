<?php
$dataFile = "adatok.txt";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = $_POST['data'] ?? '';

    if (!empty($data)) {
        file_put_contents($dataFile, $data);
        echo "Adatok frissítve.";
    } else {
        echo "Üres adat érkezett.";
    }
} else {
    echo "Csak POST kéréseket fogadok.";
}
?>
