using System;
using System.IO;
using System.IO.Ports;
using System.Text.RegularExpressions;

class Program
{
    static void Main(string[] args)
    {
        string intime = "";
        int lineCounter = 0;
        string snrValue = "N/A";
        string lastValidData = ""; // Az utolsó érdemi adat tárolására
        string dataFilePath = "adatok.txt"; // Adatok fájlja

        // Ellenőrizzük, hogy létezik-e az "adatok.txt"
        if (File.Exists(dataFilePath))
        {
            string backupFilePath = "korabbi_adatok.txt";

            // Ha már létezik "korabbi_adatok.txt", azt töröljük
            if (File.Exists(backupFilePath))
            {
                File.Delete(backupFilePath);
            }

            // "adatok.txt" átnevezése "korabbi_adatok.txt"-re
            File.Move(dataFilePath, backupFilePath);
        }

        // Adatok fájl megnyitása írásra
        using (StreamWriter dataFileWriter = new StreamWriter(dataFilePath, false))
        {
            // COM portok listázása
            Console.WriteLine("Elérhető COM portok:");
            foreach (string port in SerialPort.GetPortNames())
            {
                Console.WriteLine(port);
            }

            Console.WriteLine("Adja meg a soros port nevét (pl. COM3):");
            string portName = Console.ReadLine();

            SerialPort serialPort = new SerialPort(portName)
            {
                BaudRate = 115200,
                DataBits = 8,
                Parity = Parity.None,
                StopBits = StopBits.One,
                Handshake = Handshake.None,
                Encoding = System.Text.Encoding.ASCII,
                NewLine = "\n"
            };

            try
            {
                serialPort.Open();
                Console.WriteLine("Kapcsolódva a soros porthoz. Olvasás megkezdése...");

                // Pufferek törlése
                serialPort.DiscardInBuffer();
                serialPort.DiscardOutBuffer();

                // Alap parancsok elküldése
                serialPort.Write("sys reset\r\n");
                System.Threading.Thread.Sleep(1000); // Várakozás az újraindulásra
                                                     //serialPort.Write("radio set sf sf12\r\n");//Érzékenység
                                                     //System.Threading.Thread.Sleep(1000); // Várakozás az újraindulásra
                Console.WriteLine("Enter desired frequency");
                string freq = Console.ReadLine();
                serialPort.Write("radio set pa on\r\n");
                serialPort.Write("radio set freq " + freq+ "\r\n");
                serialPort.Write("radio set pwr 20\r\n");
                serialPort.Write("radio set bw 250\r\n");
                serialPort.Write("radio rx 0\r\n");//Vétel
                System.Threading.Thread.Sleep(500); // Várakozás az újraindulásra

                // Folyamatos olvasás
                Console.WriteLine("Nyomjon meg egy gombot a kilépéshez.");
                while (!Console.KeyAvailable)
                {
                    try
                    {
                        string line = serialPort.ReadLine();
                        lineCounter++;

                        if (line.StartsWith("radio_rx 544")) // Csak a saját adásunkat olvassuk be
                        {
                            intime = DateTime.Now.ToString("hh:mm:ss");
                            string hexData = line.Substring(9).Trim();

                            try
                            {
                                string asciiText = HexToAscii(hexData);

                                // Ellenőrzés: csak megfelelő adatok kerülhetnek fájlba
                                if (IsValidData(asciiText))
                                {
                                    string[] dataParts = asciiText.Split(',');

                                    if (dataParts.Length >= 7)
                                    {
                                        string currentData = string.Join(",", dataParts); // Érdemi adatok

                                        // Csak akkor dolgozzuk fel, ha eltér az előző érvényes érdemi adatoktól
                                        if (currentData != lastValidData)
                                        {
                                            lastValidData = currentData;

                                            asciiText = AddUnitsToData(dataParts);
                                            Console.WriteLine($"Dekódolt adat: {asciiText} , {intime} , RSSI: {snrValue}dBm");

                                            // Adatok mentése adatok.txt fájlba időbélyeggel és SNR-rel
                                            dataFileWriter.WriteLine(currentData + $"{intime},{snrValue}");
                                            dataFileWriter.Flush();

                                            // SNR lekérdezése minden 5. sor után
                                            if (lineCounter % 5 == 0)
                                            {
                                                snrValue = GetSnr(serialPort);
                                                Console.Clear();
                                            }
                                        }
                                    }
                                }
                                else
                                {
                                    Console.WriteLine($"Hiba: Nem megfelelő karaktereket tartalmaz az adat: {asciiText}");
                                }
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Hiba a feldolgozás közben: {ex.Message}");
                            }
                        }
                        else if (!string.IsNullOrEmpty(line))
                        {
                            Console.WriteLine($"Nem feldolgozható adat: {line}");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Hiba történt: {ex.Message}");
                    }
                }
            }
            catch (UnauthorizedAccessException ex)
            {
                Console.WriteLine($"Hozzáférési hiba: {ex.Message}");
            }
            catch (IOException ex)
            {
                Console.WriteLine($"I/O hiba: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Hiba történt: {ex.Message}");
            }
            finally
            {
                if (serialPort.IsOpen)
                {
                    serialPort.Close();
                }
                Console.WriteLine("Kapcsolat lezárva.");
            }
        }
    }

    private static string HexToAscii(string hexData)
    {
        System.Text.StringBuilder result = new System.Text.StringBuilder();

        for (int i = 0; i < hexData.Length; i += 2)
        {
            string hexByte = hexData.Substring(i, 2);
            int decimalValue = Convert.ToInt32(hexByte, 16);
            result.Append((char)decimalValue);
        }

        return result.ToString();
    }

    private static string AddUnitsToData(string[] dataParts)
    {
        return $"AZON: {dataParts[0]}, T: {dataParts[1]} °C, P: {dataParts[2]} hPa, AltP: {dataParts[3]} m, LAT: {dataParts[4]}, LON: {dataParts[5]}, AltG: {dataParts[6]} m";
    }

    private static string GetSnr(SerialPort serialPort)
    {
        try
        {
            //serialPort.Write("radio get snr\r\n");//Jel/Zaj arány
            serialPort.Write("radio get pktrssi\r\n");
            System.Threading.Thread.Sleep(100); // Rövid várakozás a válaszra
            string response = serialPort.ReadExisting().Trim();
            return response;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Hiba történt az SNR lekérdezése közben: {ex.Message}");
            return "Hiba";
        }
    }

    private static bool IsValidData(string data)
    {
        // Csak engedélyezett karakterek ellenőrzése
        string validPattern = @"^[TFSNA0-9.,]+$";
        return Regex.IsMatch(data, validPattern);
    }
}
