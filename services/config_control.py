import re

def get_apache_port(conf_path):
    try:
        with open(conf_path, 'r') as f:
            content = f.read()
        match = re.search(r"^Listen\s+(\d+)", content, re.MULTILINE)
        if match:
            return int(match.group(1))
        return None
    except Exception:
        return None

# def set_apache_port(conf_path, port):
#     try:
#         with open(conf_path, 'r') as f:
#             content = f.read()
#         new_content = re.sub(r"^(Listen\s+)(\d+)", f"\\1{port}", content, flags=re.MULTILINE)
#         with open(conf_path, 'w') as f:
#             f.write(new_content)
#         return True
#     except Exception:
#         return False
    
    
def set_apache_port(conf_path, port):
    try:
        with open(conf_path, 'r') as f:
            content = f.read()
        print("Before:\n", content)
        new_content = re.sub(r"^(Listen\s+)(\d+)", f"\\1{port}", content, flags=re.MULTILINE)
        print("After:\n", new_content)
        with open(conf_path, 'w') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print("Error:", e)
        return False



def get_mysql_port(conf_path):
    try:
        with open(conf_path, 'r') as f:
            content = f.read()
        match = re.search(r"port\s*=\s*(\d+)", content)
        if match:
            return int(match.group(1))
        return None
    except Exception:
        return None

def set_mysql_port(conf_path, port):
    try:
        with open(conf_path, 'r') as f:
            content = f.read()
        new_content = re.sub(r"(port\s*=\s*)(\d+)", f"\\1{port}", content)
        with open(conf_path, 'w') as f:
            f.write(new_content)
        return True
    except Exception:
        return False
