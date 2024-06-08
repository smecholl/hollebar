def find_problematic_bytes(file_path):
    with open(file_path, 'rb') as file:
        byte_position = 0
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            try:
                chunk.decode('utf-8')
            except UnicodeDecodeError as e:
                error_position = byte_position + e.start
                problematic_byte = chunk[e.start]
                print(f"Problematic byte found at position {error_position}: {problematic_byte}")
                break
            byte_position += len(chunk)

# Replace with your actual CSV file name
csv_file_path = 'cocktails_2024-06-06_18-41-22.csv'
find_problematic_bytes(csv_file_path)
