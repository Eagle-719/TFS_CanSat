<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Ellenőrizzük, hogy van-e 'flag' paraméter az adatokban
    if (isset($_POST['flag'])) {
        $flagValue = $_POST['flag'];

        // Biztonsági ellenőrzés: csak "TRUE" vagy "FALSE" értékeket fogadunk el
        if ($flagValue === 'TRUE' || $flagValue === 'FALSE') {
            $filePath = 'flag.txt';

            // Próbáljuk megírni a fájlt
            try {
                file_put_contents($filePath, $flagValue);
                http_response_code(200); // Sikeres válasz
                echo 'Flag sikeresen frissítve!';
            } catch (Exception $e) {
                http_response_code(500); // Szerver hiba
                echo 'Hiba történt a fájl írásakor: ' . $e->getMessage();
            }
        } else {
            http_response_code(400); // Rossz kérés
            echo 'Érvénytelen flag érték! Csak "TRUE" vagy "FALSE" megengedett.';
        }
    } else {
        http_response_code(400); // Rossz kérés
        echo 'Nincs flag paraméter az adatokban!';
    }
} else {
    http_response_code(405); // Nem engedélyezett HTTP metódus
    echo 'Csak POST metódus engedélyezett!';
}
?>