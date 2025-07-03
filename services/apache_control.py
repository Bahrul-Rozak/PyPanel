import subprocess

APACHE_PATH = r"C:\xampp\apache\bin\httpd.exe"

def start_apache():
    try:
        subprocess.Popen([APACHE_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Apache started successfully!"
    except Exception as e:
        return False, f"Error starting Apache: {e}"

def stop_apache():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "httpd.exe"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Apache stopped successfully!"
    except subprocess.CalledProcessError:
        return False, "Apache is not running or failed to stop."

def is_apache_running():
    try:
        # Cari proses httpd.exe
        output = subprocess.check_output("tasklist", shell=True).decode()
        return "httpd.exe" in output
    except Exception:
        return False
