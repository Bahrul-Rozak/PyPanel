import subprocess

MYSQL_PATH = r"C:\xampp\mysql\bin\mysqld.exe"

def start_mysql():
    try:
        subprocess.Popen([MYSQL_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "MySQL started successfully!"
    except Exception as e:
        return False, f"Error starting MySQL: {e}"

def stop_mysql():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "mysqld.exe"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "MySQL stopped successfully!"
    except subprocess.CalledProcessError:
        return False, "MySQL is not running or failed to stop."

def is_mysql_running():
    try:
        output = subprocess.check_output("tasklist", shell=True).decode()
        return "mysqld.exe" in output
    except Exception:
        return False
