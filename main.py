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
from PIL import Image, ImageTk
import webbrowser
import time
import psutil

APACHE_LOG_PATH = r"C:\xampp\apache\logs\error.log"
MYSQL_LOG_PATH = r"C:\xampp\mysql\data\mysql_error.log"

class PyPanel:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.update_status()
        self.update_logs()
        self.update_resource_usage()
        self.auto_start_services()
        
    def setup_ui(self):
        # Window configuration
        self.root.title("PyPanel - Alternative XAMPP Control Panel")
        self.root.geometry("1100x800")
        self.root.minsize(1000, 700)
        
        # Custom theme and styling
        self.style = ttk.Style(theme="darkly")
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        self.style.configure("Status.TLabel", font=("Segoe UI", 11))
        self.style.configure("Success.TLabel", foreground="#2ecc71")
        self.style.configure("Danger.TLabel", foreground="#e74c3c")
        self.style.configure("Info.TLabel", foreground="#3498db")
        self.style.configure("Resource.TFrame", background="#2c3e50")
        
        # Main container with padding
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header section with logo and title
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Load and display logo
        try:
            logo_img = Image.open("assets/logo.png").resize((40, 40))
            self.logo = ImageTk.PhotoImage(logo_img)
            self.logo_label = ttk.Label(self.header_frame, image=self.logo)
            self.logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except:
            pass
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="PyPanel - Alternative XAMPP Control", 
            style="Title.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Quick action buttons in header
        self.quick_actions_frame = ttk.Frame(self.header_frame)
        self.quick_actions_frame.pack(side=tk.RIGHT)
        
        self.phpmyadmin_btn = ttk.Button(
            self.quick_actions_frame,
            text="phpMyAdmin",
            bootstyle="info",
            command=lambda: webbrowser.open("http://localhost/phpmyadmin"),
            width=12
        )
        self.phpmyadmin_btn.pack(side=tk.LEFT, padx=5)
        
        self.adminer_btn = ttk.Button(
            self.quick_actions_frame,
            text="Adminer",
            bootstyle="info",
            command=lambda: webbrowser.open("http://localhost/adminer"),
            width=12
        )
        self.adminer_btn.pack(side=tk.LEFT, padx=5)
        
        # Status indicators with icons
        self.status_frame = ttk.Frame(self.header_frame)
        self.status_frame.pack(side=tk.RIGHT, padx=20)
        
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
        
        # Resource usage panel
        self.resource_frame = ttk.LabelFrame(
            self.main_frame, 
            text="System Resources", 
            bootstyle="info"
        )
        self.resource_frame.pack(fill=tk.X, pady=(0, 15))
        
        # CPU usage
        self.cpu_frame = ttk.Frame(self.resource_frame)
        self.cpu_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
        self.cpu_label = ttk.Label(self.cpu_frame, text="CPU Usage:")
        self.cpu_label.pack(side=tk.LEFT)
        
        self.cpu_usage = ttk.Label(self.cpu_frame, text="0%", style="Info.TLabel")
        self.cpu_usage.pack(side=tk.LEFT, padx=5)
        
        self.cpu_bar = ttk.Progressbar(
            self.cpu_frame, 
            orient=tk.HORIZONTAL, 
            length=150, 
            mode='determinate'
        )
        self.cpu_bar.pack(side=tk.LEFT, padx=5)
        
        # Memory usage
        self.mem_frame = ttk.Frame(self.resource_frame)
        self.mem_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
        self.mem_label = ttk.Label(self.mem_frame, text="Memory Usage:")
        self.mem_label.pack(side=tk.LEFT)
        
        self.mem_usage = ttk.Label(self.mem_frame, text="0%", style="Info.TLabel")
        self.mem_usage.pack(side=tk.LEFT, padx=5)
        
        self.mem_bar = ttk.Progressbar(
            self.mem_frame, 
            orient=tk.HORIZONTAL, 
            length=150, 
            mode='determinate'
        )
        self.mem_bar.pack(side=tk.LEFT, padx=5)
        
        # Disk usage
        self.disk_frame = ttk.Frame(self.resource_frame)
        self.disk_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
        self.disk_label = ttk.Label(self.disk_frame, text="Disk Usage:")
        self.disk_label.pack(side=tk.LEFT)
        
        self.disk_usage = ttk.Label(self.disk_frame, text="0%", style="Info.TLabel")
        self.disk_usage.pack(side=tk.LEFT, padx=5)
        
        self.disk_bar = ttk.Progressbar(
            self.disk_frame, 
            orient=tk.HORIZONTAL, 
            length=150, 
            mode='determinate'
        )
        self.disk_bar.pack(side=tk.LEFT, padx=5)
        
        # Control panels with cards layout
        self.control_panel = ttk.Frame(self.main_frame)
        self.control_panel.pack(fill=tk.X, pady=(0, 15))
        
        # Apache control card
        self.apache_frame = ttk.LabelFrame(
            self.control_panel, 
            text="Apache Server", 
            bootstyle="info"
        )
        self.apache_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.apache_btn_frame = ttk.Frame(self.apache_frame)
        self.apache_btn_frame.pack(pady=10)
        
        self.start_apache_btn = ttk.Button(
            self.apache_btn_frame, 
            text="Start Apache", 
            bootstyle="success-outline", 
            command=self.start_apache,
            width=15
        )
        self.start_apache_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_apache_btn = ttk.Button(
            self.apache_btn_frame, 
            text="Stop Apache", 
            bootstyle="danger-outline", 
            command=self.stop_apache,
            width=15
        )
        self.stop_apache_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.restart_apache_btn = ttk.Button(
            self.apache_btn_frame, 
            text="Restart Apache", 
            bootstyle="warning-outline", 
            command=self.restart_apache,
            width=15
        )
        self.restart_apache_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Apache info
        self.apache_info_frame = ttk.Frame(self.apache_frame)
        self.apache_info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.apache_test_btn = ttk.Button(
            self.apache_info_frame,
            text="Test Apache",
            bootstyle="info",
            command=self.test_apache,
            width=15
        )
        self.apache_test_btn.pack(side=tk.LEFT, padx=5)
        
        self.apache_open_btn = ttk.Button(
            self.apache_info_frame,
            text="Open Localhost",
            bootstyle="info",
            command=lambda: webbrowser.open("http://localhost"),
            width=15
        )
        self.apache_open_btn.pack(side=tk.LEFT, padx=5)
        
        # MySQL control card
        self.mysql_frame = ttk.LabelFrame(
            self.control_panel, 
            text="MySQL Server", 
            bootstyle="info"
        )
        self.mysql_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.mysql_btn_frame = ttk.Frame(self.mysql_frame)
        self.mysql_btn_frame.pack(pady=10)
        
        self.start_mysql_btn = ttk.Button(
            self.mysql_btn_frame, 
            text="Start MySQL", 
            bootstyle="success-outline", 
            command=self.start_mysql,
            width=15
        )
        self.start_mysql_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_mysql_btn = ttk.Button(
            self.mysql_btn_frame, 
            text="Stop MySQL", 
            bootstyle="danger-outline", 
            command=self.stop_mysql,
            width=15
        )
        self.stop_mysql_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.restart_mysql_btn = ttk.Button(
            self.mysql_btn_frame, 
            text="Restart MySQL", 
            bootstyle="warning-outline", 
            command=self.restart_mysql,
            width=15
        )
        self.restart_mysql_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # MySQL info
        self.mysql_info_frame = ttk.Frame(self.mysql_frame)
        self.mysql_info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.mysql_test_btn = ttk.Button(
            self.mysql_info_frame,
            text="Test MySQL",
            bootstyle="info",
            command=self.test_mysql,
            width=15
        )
        self.mysql_test_btn.pack(side=tk.LEFT, padx=5)
        
        self.mysql_cli_btn = ttk.Button(
            self.mysql_info_frame,
            text="MySQL CLI",
            bootstyle="info",
            command=self.open_mysql_cli,
            width=15
        )
        self.mysql_cli_btn.pack(side=tk.LEFT, padx=5)
        
        # Configuration panel with tabs
        self.config_notebook = ttk.Notebook(self.main_frame)
        self.config_notebook.pack(fill=tk.X, pady=(0, 15))
        
        # Port configuration tab
        self.port_tab = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.port_tab, text="Port Settings")
        
        # Apache port
        self.apache_port_frame = ttk.Frame(self.port_tab)
        self.apache_port_frame.pack(fill=tk.X, pady=5)
        
        self.apache_port_label = ttk.Label(
            self.apache_port_frame, 
            text="Apache Port:",
            width=15
        )
        self.apache_port_label.pack(side=tk.LEFT, padx=5)
        
        self.apache_port_var = tk.IntVar(
            value=config_control.get_apache_port(r"C:\xampp\apache\conf\httpd.conf") or 80
        )
        self.apache_port_entry = ttk.Entry(
            self.apache_port_frame, 
            textvariable=self.apache_port_var, 
            width=10
        )
        self.apache_port_entry.pack(side=tk.LEFT, padx=5)
        
        # MySQL port
        self.mysql_port_frame = ttk.Frame(self.port_tab)
        self.mysql_port_frame.pack(fill=tk.X, pady=5)
        
        self.mysql_port_label = ttk.Label(
            self.mysql_port_frame, 
            text="MySQL Port:",
            width=15
        )
        self.mysql_port_label.pack(side=tk.LEFT, padx=5)
        
        self.mysql_port_var = tk.IntVar(
            value=config_control.get_mysql_port(r"C:\xampp\mysql\bin\my.ini") or 3306
        )
        self.mysql_port_entry = ttk.Entry(
            self.mysql_port_frame, 
            textvariable=self.mysql_port_var, 
            width=10
        )
        self.mysql_port_entry.pack(side=tk.LEFT, padx=5)
        
        # Save button
        self.save_ports_btn = ttk.Button(
            self.port_tab, 
            text="Save Port Settings", 
            bootstyle="primary", 
            command=self.save_ports,
            width=20
        )
        self.save_ports_btn.pack(pady=10)
        
        # Path configuration tab
        self.path_tab = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.path_tab, text="Path Settings")
        
        # htdocs configuration
        self.htdocs_frame = ttk.Frame(self.path_tab)
        self.htdocs_frame.pack(fill=tk.X, pady=10)
        
        self.choose_htdocs_btn = ttk.Button(
            self.htdocs_frame, 
            text="Select htdocs Folder", 
            command=self.choose_htdocs,
            width=20
        )
        self.choose_htdocs_btn.pack(side=tk.LEFT, padx=5)
        
        config_data = config.load_config()
        self.htdocs_label = ttk.Label(
            self.htdocs_frame, 
            text=f"Current: {config_data.get('htdocs_path', 'Not selected')}",
            font=("Segoe UI", 9)
        )
        self.htdocs_label.pack(side=tk.LEFT, padx=5)
        
        # Open htdocs button
        self.open_htdocs_btn = ttk.Button(
            self.htdocs_frame,
            text="Open htdocs",
            command=self.open_htdocs,
            width=20
        )
        self.open_htdocs_btn.pack(side=tk.LEFT, padx=5)
        
        # Auto-start configuration tab
        self.auto_tab = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.auto_tab, text="Auto Settings")
        
        # Auto-start checkbox
        self.auto_start_var = tk.BooleanVar(value=True)
        self.auto_start_check = ttk.Checkbutton(
            self.auto_tab, 
            text="Auto Start Services on Launch", 
            variable=self.auto_start_var,
            bootstyle="primary-round-toggle"
        )
        self.auto_start_check.pack(anchor='w', pady=10)
        
        # Log tabs with search functionality
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Apache log tab
        self.apache_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.apache_tab, text="Apache Logs")
        
        # Apache log toolbar
        self.apache_log_toolbar = ttk.Frame(self.apache_tab)
        self.apache_log_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.apache_log_search_label = ttk.Label(self.apache_log_toolbar, text="Search:")
        self.apache_log_search_label.pack(side=tk.LEFT, padx=5)
        
        self.apache_log_search_var = tk.StringVar()
        self.apache_log_search_entry = ttk.Entry(
            self.apache_log_toolbar, 
            textvariable=self.apache_log_search_var,
            width=30
        )
        self.apache_log_search_entry.pack(side=tk.LEFT, padx=5)
        
        self.apache_log_search_btn = ttk.Button(
            self.apache_log_toolbar,
            text="Find",
            command=lambda: self.search_log("apache"),
            bootstyle="info",
            width=10
        )
        self.apache_log_search_btn.pack(side=tk.LEFT, padx=5)
        
        self.apache_log_clear_btn = ttk.Button(
            self.apache_log_toolbar,
            text="Clear",
            command=lambda: self.clear_log("apache"),
            bootstyle="secondary",
            width=10
        )
        self.apache_log_clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.apache_log_refresh_btn = ttk.Button(
            self.apache_log_toolbar,
            text="Refresh",
            command=lambda: self.refresh_log("apache"),
            bootstyle="secondary",
            width=10
        )
        self.apache_log_refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Apache log content
        self.apache_log_frame = ttk.Frame(self.apache_tab)
        self.apache_log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.apache_log_text = tk.Text(
            self.apache_log_frame, 
            wrap='none', 
            font=("Consolas", 10),
            bg="#222222",
            fg="#ffffff",
            insertbackground="white"
        )
        self.apache_log_scroll = ttk.Scrollbar(
            self.apache_log_frame, 
            command=self.apache_log_text.yview
        )
        self.apache_log_text.configure(yscrollcommand=self.apache_log_scroll.set)
        
        self.apache_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.apache_log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # MySQL log tab
        self.mysql_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.mysql_tab, text="MySQL Logs")
        
        # MySQL log toolbar
        self.mysql_log_toolbar = ttk.Frame(self.mysql_tab)
        self.mysql_log_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.mysql_log_search_label = ttk.Label(self.mysql_log_toolbar, text="Search:")
        self.mysql_log_search_label.pack(side=tk.LEFT, padx=5)
        
        self.mysql_log_search_var = tk.StringVar()
        self.mysql_log_search_entry = ttk.Entry(
            self.mysql_log_toolbar, 
            textvariable=self.mysql_log_search_var,
            width=30
        )
        self.mysql_log_search_entry.pack(side=tk.LEFT, padx=5)
        
        self.mysql_log_search_btn = ttk.Button(
            self.mysql_log_toolbar,
            text="Find",
            command=lambda: self.search_log("mysql"),
            bootstyle="info",
            width=10
        )
        self.mysql_log_search_btn.pack(side=tk.LEFT, padx=5)
        
        self.mysql_log_clear_btn = ttk.Button(
            self.mysql_log_toolbar,
            text="Clear",
            command=lambda: self.clear_log("mysql"),
            bootstyle="secondary",
            width=10
        )
        self.mysql_log_clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.mysql_log_refresh_btn = ttk.Button(
            self.mysql_log_toolbar,
            text="Refresh",
            command=lambda: self.refresh_log("mysql"),
            bootstyle="secondary",
            width=10
        )
        self.mysql_log_refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # MySQL log content
        self.mysql_log_frame = ttk.Frame(self.mysql_tab)
        self.mysql_log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.mysql_log_text = tk.Text(
            self.mysql_log_frame, 
            wrap='none', 
            font=("Consolas", 10),
            bg="#222222",
            fg="#ffffff",
            insertbackground="white"
        )
        self.mysql_log_scroll = ttk.Scrollbar(
            self.mysql_log_frame, 
            command=self.mysql_log_text.yview
        )
        self.mysql_log_text.configure(yscrollcommand=self.mysql_log_scroll.set)
        
        self.mysql_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.mysql_log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar with time
        self.status_bar = ttk.Frame(self.root, height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            self.status_bar, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.time_label = ttk.Label(
            self.status_bar,
            text="",
            relief=tk.SUNKEN,
            anchor=tk.E
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Update time
        self.update_time()
    
    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%Y-%m-%d")
        self.time_label.config(text=f"{current_date} {current_time}")
        self.root.after(1000, self.update_time)
    
    def update_resource_usage(self):
        # CPU usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_usage.config(text=f"{cpu_percent}%")
        self.cpu_bar['value'] = cpu_percent
        
        # Memory usage
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        self.mem_usage.config(text=f"{mem_percent}%")
        self.mem_bar['value'] = mem_percent
        
        # Disk usage (C: drive)
        try:
            disk = psutil.disk_usage('C:\\')
            disk_percent = disk.percent
            self.disk_usage.config(text=f"{disk_percent}%")
            self.disk_bar['value'] = disk_percent
        except:
            pass
        
        self.root.after(2000, self.update_resource_usage)
    
    def start_apache(self):
        self.status_label.config(text="Starting Apache...")
        threading.Thread(target=self._start_apache_thread, daemon=True).start()
    
    def _start_apache_thread(self):
        success, message = apache_control.start_apache()
        if success:
            self.root.after(0, lambda: messagebox.showinfo("Success", message))
            self.root.after(0, lambda: self.status_label.config(text="Apache started successfully"))
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", message))
            self.root.after(0, lambda: self.status_label.config(text="Failed to start Apache"))
        self.root.after(0, self.update_status)

    def stop_apache(self):
        self.status_label.config(text="Stopping Apache...")
        threading.Thread(target=self._stop_apache_thread, daemon=True).start()
    
    def _stop_apache_thread(self):
        success, message = apache_control.stop_apache()
        if success:
            self.root.after(0, lambda: messagebox.showinfo("Success", message))
            self.root.after(0, lambda: self.status_label.config(text="Apache stopped successfully"))
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", message))
            self.root.after(0, lambda: self.status_label.config(text="Failed to stop Apache"))
        self.root.after(0, self.update_status)
        
    def restart_apache(self):
        self.status_label.config(text="Restarting Apache...")
        threading.Thread(target=self._restart_apache_thread, daemon=True).start()
    
    def _restart_apache_thread(self):
        _, _ = apache_control.stop_apache()
        time.sleep(1)  # Give it a second to stop
        success, message = apache_control.start_apache()
        if success:
            self.root.after(0, lambda: messagebox.showinfo("Success", "Apache restarted successfully"))
            self.root.after(0, lambda: self.status_label.config(text="Apache restarted successfully"))
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", "Failed to restart Apache"))
            self.root.after(0, lambda: self.status_label.config(text="Failed to restart Apache"))
        self.root.after(0, self.update_status)
        
    def start_mysql(self):
        self.status_label.config(text="Starting MySQL...")
        threading.Thread(target=self._start_mysql_thread, daemon=True).start()
    
    def _start_mysql_thread(self):
        success, message = mysql_control.start_mysql()
        if success:
            self.root.after(0, lambda: messagebox.showinfo("Success", message))
            self.root.after(0, lambda: self.status_label.config(text="MySQL started successfully"))
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", message))
            self.root.after(0, lambda: self.status_label.config(text="Failed to start MySQL"))
        self.root.after(0, self.update_status)

    def stop_mysql(self):
        self.status_label.config(text="Stopping MySQL...")
        threading.Thread(target=self._stop_mysql_thread, daemon=True).start()
    
    def _stop_mysql_thread(self):
        success, message = mysql_control.stop_mysql()
        if success:
            self.root.after(0, lambda: messagebox.showinfo("Success", message))
            self.root.after(0, lambda: self.status_label.config(text="MySQL stopped successfully"))
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", message))
            self.root.after(0, lambda: self.status_label.config(text="Failed to stop MySQL"))
        self.root.after(0, self.update_status)
        
    def restart_mysql(self):
        self.status_label.config(text="Restarting MySQL...")
        threading.Thread(target=self._restart_mysql_thread, daemon=True).start()
    
    def _restart_mysql_thread(self):
        _, _ = mysql_control.stop_mysql()
        time.sleep(3)  # MySQL needs more time to stop
        success, message = mysql_control.start_mysql()
        if success:
            self.root.after(0, lambda: messagebox.showinfo("Success", "MySQL restarted successfully"))
            self.root.after(0, lambda: self.status_label.config(text="MySQL restarted successfully"))
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", "Failed to restart MySQL"))
            self.root.after(0, lambda: self.status_label.config(text="Failed to restart MySQL"))
        self.root.after(0, self.update_status)
        
    def test_apache(self):
        self.status_label.config(text="Testing Apache...")
        threading.Thread(target=self._test_apache_thread, daemon=True).start()
    
    def _test_apache_thread(self):
        if apache_control.is_apache_running():
            self.root.after(0, lambda: messagebox.showinfo("Test", "Apache is running"))
            self.root.after(0, lambda: self.status_label.config(text="Apache test: Running"))
        else:
            self.root.after(0, lambda: messagebox.showinfo("Test", "Apache is not running"))
            self.root.after(0, lambda: self.status_label.config(text="Apache test: Not running"))
    
    def test_mysql(self):
        self.status_label.config(text="Testing MySQL...")
        threading.Thread(target=self._test_mysql_thread, daemon=True).start()
    
    def _test_mysql_thread(self):
        if mysql_control.is_mysql_running():
            self.root.after(0, lambda: messagebox.showinfo("Test", "MySQL is running"))
            self.root.after(0, lambda: self.status_label.config(text="MySQL test: Running"))
        else:
            self.root.after(0, lambda: messagebox.showinfo("Test", "MySQL is not running"))
            self.root.after(0, lambda: self.status_label.config(text="MySQL test: Not running"))
    
    def open_mysql_cli(self):
        try:
            os.system("start cmd /k mysql -u root")
            self.status_label.config(text="Opened MySQL command line")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open MySQL CLI: {str(e)}")
            self.status_label.config(text="Failed to open MySQL CLI")
        
    def update_status(self):
        if apache_control.is_apache_running():
            self.apache_status_label.config(
                text="Apache: ✅ Running", 
                style="Success.TLabel"
            )
            self.start_apache_btn.config(state="disabled")
            self.stop_apache_btn.config(state="normal")
            self.restart_apache_btn.config(state="normal")
        else:
            self.apache_status_label.config(
                text="Apache: ❌ Stopped", 
                style="Danger.TLabel"
            )
            self.start_apache_btn.config(state="normal")
            self.stop_apache_btn.config(state="disabled")
            self.restart_apache_btn.config(state="disabled")

        if mysql_control.is_mysql_running():
            self.mysql_status_label.config(
                text="MySQL: ✅ Running", 
                style="Success.TLabel"
            )
            self.start_mysql_btn.config(state="disabled")
            self.stop_mysql_btn.config(state="normal")
            self.restart_mysql_btn.config(state="normal")
        else:
            self.mysql_status_label.config(
                text="MySQL: ❌ Stopped", 
                style="Danger.TLabel"
            )
            self.start_mysql_btn.config(state="normal")
            self.stop_mysql_btn.config(state="disabled")
            self.restart_mysql_btn.config(state="disabled")

        self.root.after(2000, self.update_status)

    def update_logs(self):
        threading.Thread(target=self._update_logs_thread, daemon=True).start()
        self.root.after(5000, self.update_logs)
    
    def _update_logs_thread(self):
        apache_log = log_reader.read_log(APACHE_LOG_PATH)
        mysql_log = log_reader.read_log(MYSQL_LOG_PATH)
        
        self.root.after(0, lambda: self._update_log_text(self.apache_log_text, apache_log))
        self.root.after(0, lambda: self._update_log_text(self.mysql_log_text, mysql_log))
    
    def _update_log_text(self, widget, content):
        widget.config(state="normal")
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, content)
        widget.see(tk.END)
        widget.config(state="disabled")
    
    def search_log(self, log_type):
        search_term = self.apache_log_search_var.get() if log_type == "apache" else self.mysql_log_search_var.get()
        text_widget = self.apache_log_text if log_type == "apache" else self.mysql_log_text
        
        if not search_term:
            return
            
        text_widget.tag_remove("search", "1.0", tk.END)
        
        start = "1.0"
        found = False
        
        while True:
            pos = text_widget.search(search_term, start, stopindex=tk.END)
            if not pos:
                break
                
            end = f"{pos}+{len(search_term)}c"
            text_widget.tag_add("search", pos, end)
            start = end
            found = True
            
        text_widget.tag_config("search", background="yellow", foreground="black")
        
        if found:
            text_widget.see(pos)
            self.status_label.config(text=f"Found '{search_term}' in {log_type} logs")
        else:
            self.status_label.config(text=f"'{search_term}' not found in {log_type} logs")
    
    def clear_log(self, log_type):
        if log_type == "apache":
            self.apache_log_text.config(state="normal")
            self.apache_log_text.delete(1.0, tk.END)
            self.apache_log_text.config(state="disabled")
        else:
            self.mysql_log_text.config(state="normal")
            self.mysql_log_text.delete(1.0, tk.END)
            self.mysql_log_text.config(state="disabled")
        
        self.status_label.config(text=f"Cleared {log_type} log display")
    
    def refresh_log(self, log_type):
        self.status_label.config(text=f"Refreshing {log_type} logs...")
        if log_type == "apache":
            log_content = log_reader.read_log(APACHE_LOG_PATH)
            self._update_log_text(self.apache_log_text, log_content)
        else:
            log_content = log_reader.read_log(MYSQL_LOG_PATH)
            self._update_log_text(self.mysql_log_text, log_content)
        
        self.status_label.config(text=f"Refreshed {log_type} logs")
    
    def choose_htdocs(self):
        folder = fd.askdirectory()
        if folder:
            config_data = config.load_config()
            config_data["htdocs_path"] = folder
            config.save_config(config_data)
            self.htdocs_label.config(text=f"Current: {folder}")
            self.status_label.config(text=f"htdocs folder set to: {folder}")
    
    def open_htdocs(self):
        config_data = config.load_config()
        htdocs_path = config_data.get("htdocs_path")
        
        if htdocs_path and os.path.exists(htdocs_path):
            try:
                os.startfile(htdocs_path)
                self.status_label.config(text=f"Opened htdocs folder: {htdocs_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
                self.status_label.config(text=f"Failed to open htdocs folder")
        else:
            messagebox.showerror("Error", "htdocs folder not selected or doesn't exist")
            self.status_label.config(text="htdocs folder not selected or doesn't exist")
    
    def auto_start_services(self):
        if self.auto_start_var.get():
            self.status_label.config(text="Auto-starting services...")
            
            def auto_start_thread():
                if not apache_control.is_apache_running():
                    apache_control.start_apache()
                
                if not mysql_control.is_mysql_running():
                    mysql_control.start_mysql()
                
                self.root.after(0, lambda: self.status_label.config(text="Auto-start completed"))
                self.root.after(0, self.update_status)
            
            threading.Thread(target=auto_start_thread, daemon=True).start()
    
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