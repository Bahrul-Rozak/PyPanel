def read_log(path, max_lines=100):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Ambil max_lines baris terakhir
            return "".join(lines[-max_lines:])
    except Exception as e:
        return f"Failed to read log: {e}"
