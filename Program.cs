using System;
using System.IO.Ports;
using System.Text;

class Program
{
    private static StringBuilder dataBuffer = new StringBuilder();

    static void Main(string[] args)
    {
        Console.WriteLine("Adja meg a soros port nevét (pl. COM3):");
        string portName = Console.ReadLine();

        SerialPort serialPort = new SerialPort(portName)
        {
            BaudRate = 115200,         // Állítsd be a megfelelő adatátviteli sebességet
            DataBits = 8,           // Alapértelmezett adatbit szám
            Parity = Parity.None,   // Nincs paritás
            StopBits = StopBits.One, // Egy stopbit
            Encoding = Encoding.ASCII, // Biztosítja, hogy az adatok megfelelően legyenek dekódolva
            NewLine = "\n"         // Sorvég jel meghatározása
        };

        try
        {
            serialPort.Open();
            Console.WriteLine("Kapcsolódva a soros porthoz.");

            // Kiírja a reset és rádió parancsokat
            serialPort.WriteLine("sys reset");
            serialPort.WriteLine("radio rx 0");

            serialPort.DataReceived += SerialPort_DataReceived;
            Console.WriteLine("Nyomj meg egy gombot a kilépéshez.");
            Console.ReadKey();
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
            Console.WriteLine("A program véget ért.");
        }
    }

    private static void SerialPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
    {
        SerialPort sp = (SerialPort)sender;
        string incomingData = sp.ReadExisting();

        try
        {
            dataBuffer.Append(incomingData);

            while (dataBuffer.ToString().Contains("\n"))
            {
                string fullLine = ExtractLineFromBuffer();
                ProcessLine(fullLine);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Hiba a bejövő adat feldolgozása közben: {ex.Message}");
        }
    }

    private static string ExtractLineFromBuffer()
    {
        string bufferContent = dataBuffer.ToString();
        int lineEndIndex = bufferContent.IndexOf('\n');
        string fullLine = bufferContent.Substring(0, lineEndIndex).Trim();
        dataBuffer.Remove(0, lineEndIndex + 1);
        return fullLine;
    }

    private static void ProcessLine(string line)
    {
        if (line.StartsWith("radio_rx "))
        {
            string hexData = line.Substring(9).Trim();

            try
            {
                // Hex string ASCII szöveggé alakítása
                string asciiText = HexToAscii(hexData);

                // Eredmény kiírása a konzolra
                Console.WriteLine(asciiText);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Hiba a hex adat feldolgozása közben: {ex.Message}");
            }
        }
        else
        {
            Console.WriteLine("Ismeretlen adat: " + line);
        }
    }

    private static string HexToAscii(string hexData)
    {
        StringBuilder result = new StringBuilder();

        for (int i = 0; i < hexData.Length; i += 2)
        {
            string hexByte = hexData.Substring(i, 2);
            int decimalValue = Convert.ToInt32(hexByte, 16);
            result.Append((char)decimalValue);
        }

        return result.ToString();
    }
}
