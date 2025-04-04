def process_txt(input_file, output_file):

    with open(input_file, mode='r') as infile:
        lines = infile.readlines()

    with open(output_file, mode='w') as outfile:
        for line in lines:
            line = line.strip()
            
            id, temp, pressure, humidity, lat, long, hnt, radio = line.split(',')
            
            try:
                lat = float(lat)
                lat = coord(lat)
                long = float(long)
                long = coord(long)
            except Exception as e:
                print(f"An error occurred: {e}")
                
            modified_value = hnt[:5] + ',' + hnt[5:]
            height, timestamp = modified_value.split(',')

            new_line = f"{id},{temp},{pressure},{humidity},{lat},{long},{height},{timestamp},{radio}"
            outfile.write(new_line + "\n")

def coord(coord):
    degrees = int(coord)
    minutes_decimal = coord - degrees
    
    minutes = minutes_decimal * 100.0

    decimal_degrees = degrees + minutes / 60.0
    decimal_degrees = round(decimal_degrees, 5)
    return decimal_degrees

process_txt("data_f_clean.txt", "converted_data.txt")