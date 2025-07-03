import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from services import apache_control
from services import mysql_control
import threading
from services import log_reader
import os
import tkinter.filedialog as fd
import config
from services import config_control

APACHE_LOG_PATH = r"C:\xampp\apache\logs\error.log"
MYSQL_LOG_PATH = r"C:\xampp\mysql\data\mysql_error.log"

class PyPanel:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.update_status()
        self.update_logs()
        self.auto_start_services()
        
    def setup_ui(self):
        # Window configuration
        self.root.title("PyPanel - Alternative XAMPP Control Panel")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Custom theme colors
        self.style = ttk.Style(theme="darkly")
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        self.style.configure("Status.TLabel", font=("Segoe UI", 11))
        self.style.configure("Success.TLabel", foreground="#2ecc71")
        self.style.configure("Danger.TLabel", foreground="#e74c3c")
        
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header section
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="PyPanel - Alternative XAMPP Control Panel", 
            style="Title.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Status indicators
        self.status_frame = ttk.Frame(self.header_frame)
        self.status_frame.pack(side=tk.RIGHT)
        
        self.apache_status_label = ttk.Label(
            self.status_frame, 
            text="Apache: ❌", 
            style="Status.TLabel"
        )
        self.apache_status_label.pack(side=tk.LEFT, padx=5)
        
        self.mysql_status_label = ttk.Label(
            self.status_frame, 
            text="MySQL: ❌", 
            style="Status.TLabel"
        )
        self.mysql_status_label.pack(side=tk.LEFT, padx=5)
        
        # Control panels
        self.control_panel = ttk.Frame(self.main_frame)
        self.control_panel.pack(fill=tk.X, pady=(0, 15))
        
        # Apache control
        self.apache_frame = ttk.LabelFrame(
            self.control_panel, 
            text="Apache Server", 
            bootstyle="info"
        )
        self.apache_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.apache_btn_frame = ttk.Frame(self.apache_frame)
        self.apache_btn_frame.pack(pady=5)
        
        self.start_apache_btn = ttk.Button(
            self.apache_btn_frame, 
            text="Start Apache", 
            bootstyle="success", 
            command=self.start_apache,
            width=12
        )
        self.start_apache_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_apache_btn = ttk.Button(
            self.apache_btn_frame, 
            text="Stop Apache", 
            bootstyle="danger", 
            command=self.stop_apache,
            width=12
        )
        self.stop_apache_btn.pack(side=tk.LEFT, padx=5)
        
        # MySQL control
        self.mysql_frame = ttk.LabelFrame(
            self.control_panel, 
            text="MySQL Server", 
            bootstyle="info"
        )
        self.mysql_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.mysql_btn_frame = ttk.Frame(self.mysql_frame)
        self.mysql_btn_frame.pack(pady=5)
        
        self.start_mysql_btn = ttk.Button(
            self.mysql_btn_frame, 
            text="Start MySQL", 
            bootstyle="success", 
            command=self.start_mysql,
            width=12
        )
        self.start_mysql_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_mysql_btn = ttk.Button(
            self.mysql_btn_frame, 
            text="Stop MySQL", 
            bootstyle="danger", 
            command=self.stop_mysql,
            width=12
        )
        self.stop_mysql_btn.pack(side=tk.LEFT, padx=5)
        
        # Configuration panel
        self.config_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Configuration", 
            bootstyle="primary"
        )
        self.config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Port configuration
        self.port_frame = ttk.Frame(self.config_frame)
        self.port_frame.pack(fill=tk.X, pady=5)
        
        # Apache port
        self.apache_port_label = ttk.Label(
            self.port_frame, 
            text="Apache Port:"
        )
        self.apache_port_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.apache_port_var = tk.IntVar(
            value=config_control.get_apache_port(r"C:\xampp\apache\conf\httpd.conf") or 80
        )
        self.apache_port_entry = ttk.Entry(
            self.port_frame, 
            textvariable=self.apache_port_var, 
            width=10
        )
        self.apache_port_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # MySQL port
        self.mysql_port_label = ttk.Label(
            self.port_frame, 
            text="MySQL Port:"
        )
        self.mysql_port_label.grid(row=0, column=2, padx=(20,5), pady=5, sticky='w')
        
        self.mysql_port_var = tk.IntVar(
            value=config_control.get_mysql_port(r"C:\xampp\mysql\bin\my.ini") or 3306
        )
        self.mysql_port_entry = ttk.Entry(
            self.port_frame, 
            textvariable=self.mysql_port_var, 
            width=10
        )
        self.mysql_port_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        self.save_ports_btn = ttk.Button(
            self.port_frame, 
            text="Save Ports", 
            bootstyle="primary", 
            command=self.save_ports,
            width=12
        )
        self.save_ports_btn.grid(row=0, column=4, padx=10, pady=5, sticky='e')
        
        # htdocs configuration
        self.htdocs_frame = ttk.Frame(self.config_frame)
        self.htdocs_frame.pack(fill=tk.X, pady=5)
        
        self.choose_htdocs_btn = ttk.Button(
            self.htdocs_frame, 
            text="Select htdocs Folder", 
            command=self.choose_htdocs,
            width=15
        )
        self.choose_htdocs_btn.pack(side=tk.LEFT, padx=5)
        
        config_data = config.load_config()
        self.htdocs_label = ttk.Label(
            self.htdocs_frame, 
            text=f"Current: {config_data.get('htdocs_path', 'Not selected')}",
            font=("Segoe UI", 9)
        )
        self.htdocs_label.pack(side=tk.LEFT, padx=5)
        
        # Auto-start checkbox
        self.auto_start_var = tk.BooleanVar(value=True)
        self.auto_start_check = ttk.Checkbutton(
            self.config_frame, 
            text="Auto Start Services on Launch", 
            variable=self.auto_start_var
        )
        self.auto_start_check.pack(anchor='w', pady=5)
        
        # Log tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Apache log tab
        self.apache_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.apache_tab, text="Apache Logs")
        
        self.apache_log_text = tk.Text(
            self.apache_tab, 
            wrap='none', 
            font=("Consolas", 10),
            bg="#222222",
            fg="#ffffff",
            insertbackground="white"
        )
        self.apache_log_scroll = ttk.Scrollbar(
            self.apache_tab, 
            command=self.apache_log_text.yview
        )
        self.apache_log_text.configure(yscrollcommand=self.apache_log_scroll.set)
        
        self.apache_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.apache_log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # MySQL log tab
        self.mysql_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.mysql_tab, text="MySQL Logs")
        
        self.mysql_log_text = tk.Text(
            self.mysql_tab, 
            wrap='none', 
            font=("Consolas", 10),
            bg="#222222",
            fg="#ffffff",
            insertbackground="white"
        )
        self.mysql_log_scroll = ttk.Scrollbar(
            self.mysql_tab, 
            command=self.mysql_log_text.yview
        )
        self.mysql_log_text.configure(yscrollcommand=self.mysql_log_scroll.set)
        
        self.mysql_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.mysql_log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_bar = ttk.Frame(self.root, height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = ttk.Label(
            self.status_bar, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)
    
    def start_apache(self):
        self.status_label.config(text="Starting Apache...")
        success, message = apache_control.start_apache()
        if success:
            messagebox.showinfo("Success", message)
            self.status_label.config(text="Apache started successfully")
        else:
            messagebox.showerror("Error", message)
            self.status_label.config(text="Failed to start Apache")
        self.update_status()

    def stop_apache(self):
        self.status_label.config(text="Stopping Apache...")
        success, message = apache_control.stop_apache()
        if success:
            messagebox.showinfo("Success", message)
            self.status_label.config(text="Apache stopped successfully")
        else:
            messagebox.showerror("Error", message)
            self.status_label.config(text="Failed to stop Apache")
        self.update_status()
        
    def start_mysql(self):
        self.status_label.config(text="Starting MySQL...")
        success, message = mysql_control.start_mysql()
        if success:
            messagebox.showinfo("Success", message)
            self.status_label.config(text="MySQL started successfully")
        else:
            messagebox.showerror("Error", message)
            self.status_label.config(text="Failed to start MySQL")
        self.update_status()

    def stop_mysql(self):
        self.status_label.config(text="Stopping MySQL...")
        success, message = mysql_control.stop_mysql()
        if success:
            messagebox.showinfo("Success", message)
            self.status_label.config(text="MySQL stopped successfully")
        else:
            messagebox.showerror("Error", message)
            self.status_label.config(text="Failed to stop MySQL")
        self.update_status()
        
    def update_status(self):
        if apache_control.is_apache_running():
            self.apache_status_label.config(
                text="Apache: ✅ Running", 
                style="Success.TLabel"
            )
        else:
            self.apache_status_label.config(
                text="Apache: ❌ Stopped", 
                style="Danger.TLabel"
            )

        if mysql_control.is_mysql_running():
            self.mysql_status_label.config(
                text="MySQL: ✅ Running", 
                style="Success.TLabel"
            )
        else:
            self.mysql_status_label.config(
                text="MySQL: ❌ Stopped", 
                style="Danger.TLabel"
            )

        self.root.after(2000, self.update_status)

    def update_logs(self):
        apache_log = log_reader.read_log(APACHE_LOG_PATH)
        mysql_log = log_reader.read_log(MYSQL_LOG_PATH)

        self.apache_log_text.delete(1.0, tk.END)
        self.apache_log_text.insert(tk.END, apache_log)
        self.apache_log_text.see(tk.END)

        self.mysql_log_text.delete(1.0, tk.END)
        self.mysql_log_text.insert(tk.END, mysql_log)
        self.mysql_log_text.see(tk.END)

        self.root.after(5000, self.update_logs)
    
    def choose_htdocs(self):
        folder = fd.askdirectory()
        if folder:
            config_data = config.load_config()
            config_data["htdocs_path"] = folder
            config.save_config(config_data)
            self.htdocs_label.config(text=f"Current: {folder}")
            self.status_label.config(text=f"htdocs folder set to: {folder}")
            
    def auto_start_services(self):
        if self.auto_start_var.get():
            if not apache_control.is_apache_running():
                apache_control.start_apache()

            if not mysql_control.is_mysql_running():
                mysql_control.start_mysql()
    
    def save_ports(self):
        apache_conf = r"C:\xampp\apache\conf\httpd.conf"
        mysql_conf = r"C:\xampp\mysql\bin\my.ini"

        ap = self.apache_port_var.get()
        mp = self.mysql_port_var.get()

        a_res = config_control.set_apache_port(apache_conf, ap)
        m_res = config_control.set_mysql_port(mysql_conf, mp)

        if a_res and m_res:
            messagebox.showinfo("Success", "Ports updated successfully! Please restart services.")
            self.status_label.config(text="Ports updated - restart services to apply changes")
        else:
            messagebox.showerror("Error", "Failed to update ports.")
            self.status_label.config(text="Failed to update ports")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = PyPanel(root)
    root.mainloop()