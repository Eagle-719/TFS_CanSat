def filter_lines(input_file, output_file, prefix):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                if line.startswith(prefix):
                    outfile.write(line)
        print(f"Filtered lines written to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

filter_lines("data_final.txt", "data_f_clean.txt", "TFS")