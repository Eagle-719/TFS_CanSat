<?php
set_time_limit(0); // Ne legyen időkorlát
$flagFile = __DIR__ . "\\flag.txt"; // Flag fájl útvonala
$serverUrl = "https://burger.hu";
$dataFile = __DIR__ . "\\adatok.txt";
$logFile = __DIR__ . "\\send_data.log";
$counter = 0;

while (true) {
    // Flag fájl tartalmának beolvasása
    $flag = trim(@file_get_contents($flagFile));

    if ($flag === 'TRUE') {
        $counter++;
        $statusMessage = "";

        if (file_exists($dataFile)) {
            $data = file_get_contents($dataFile);

            if (!empty($data)) {
                $ch = curl_init($serverUrl);
                curl_setopt($ch, CURLOPT_POST, 1);
                curl_setopt($ch, CURLOPT_POSTFIELDS, ['data' => $data]);
                curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

                $response = curl_exec($ch);
                $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

                if (curl_errno($ch)) {
                    $statusMessage = "Hiba a küldés során: " . curl_error($ch);
                } else {
                    $statusMessage = "Sikeres küldés #$counter: HTTP $httpCode, Válasz: $response";
                }

                curl_close($ch);
            } else {
                $statusMessage = "Az adatok üresek, nincs mit küldeni.";
            }
        } else {
            $statusMessage = "Fájl nem található: $dataFile";
        }

        // Naplózzuk az eredményt és kiírjuk konzolra
        file_put_contents($logFile, date('[Y-m-d H:i:s]') . " $statusMessage\n", FILE_APPEND);
        echo date('[Y-m-d H:i:s]') . " $statusMessage\n";
    } elseif ($flag === 'FALSE') {
        echo date('[Y-m-d H:i:s]') . " Adatküldés szüneteltetve.\n";
        sleep(5); // 5 másodperc szünet a flag következő vizsgálatáig
    } else {
        echo date('[Y-m-d H:i:s]') . " Érvénytelen flag érték: $flag\n";
    }

    // Kimenet azonnali megjelenítése
    ob_flush();
    flush();

    if ($flag === 'TRUE') {
        usleep(2000000); // 2 másodperc szünet az adatküldések között
    }
}
?>
