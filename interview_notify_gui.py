#!/usr/bin/env python3

"""
GUI wrapper for interview-notify-advanced
Provides a user-friendly interface for configuring and running the notifier
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import threading
import json
from pathlib import Path
import sys
import queue

VERSION = '1.4.0'
CONFIG_FILE = Path.home() / '.interview-notify-config.json'


class InterviewNotifyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Interview Notify Advanced v{VERSION}")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        self.process = None
        self.log_queue = queue.Queue()
        self.log_dirs = []

        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # === Configuration Section ===
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=5)
        config_frame.columnconfigure(1, weight=1)

        # Topic
        ttk.Label(config_frame, text="ntfy Topic:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.topic_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.topic_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)

        # Server
        ttk.Label(config_frame, text="ntfy Server:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.server_var = tk.StringVar(value="https://ntfy.sh/")
        ttk.Entry(config_frame, textvariable=self.server_var, width=30).grid(row=0, column=3, sticky=(tk.W, tk.E), pady=2, padx=5)

        # Nick
        ttk.Label(config_frame, text="Your Nick:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.nick_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.nick_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)

        # Bot Nicks
        ttk.Label(config_frame, text="Bot Nicks:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.bot_nicks_var = tk.StringVar(value="Gatekeeper")
        ttk.Entry(config_frame, textvariable=self.bot_nicks_var, width=30).grid(row=1, column=3, sticky=(tk.W, tk.E), pady=2, padx=5)

        # Mode
        ttk.Label(config_frame, text="Mode:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.mode_var = tk.StringVar(value="red")
        mode_combo = ttk.Combobox(config_frame, textvariable=self.mode_var, values=["red", "ops"], state="readonly", width=10)
        mode_combo.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)

        # Rate Limit
        ttk.Label(config_frame, text="Rate Limit (sec):").grid(row=2, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.rate_limit_var = tk.StringVar(value="60")
        ttk.Entry(config_frame, textvariable=self.rate_limit_var, width=10).grid(row=2, column=3, sticky=tk.W, pady=2, padx=5)

        # Log Directories
        ttk.Label(config_frame, text="Log Directories:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=2)

        log_dir_frame = ttk.Frame(config_frame)
        log_dir_frame.grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2, padx=5)
        log_dir_frame.columnconfigure(0, weight=1)

        self.log_dir_listbox = tk.Listbox(log_dir_frame, height=3)
        self.log_dir_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        log_dir_scrollbar = ttk.Scrollbar(log_dir_frame, orient=tk.VERTICAL, command=self.log_dir_listbox.yview)
        log_dir_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_dir_listbox.configure(yscrollcommand=log_dir_scrollbar.set)

        log_dir_buttons = ttk.Frame(log_dir_frame)
        log_dir_buttons.grid(row=0, column=2, sticky=(tk.N), padx=5)
        ttk.Button(log_dir_buttons, text="Add", command=self.add_log_dir, width=8).pack(pady=2)
        ttk.Button(log_dir_buttons, text="Remove", command=self.remove_log_dir, width=8).pack(pady=2)

        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=5)

        self.check_bot_nicks_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Check bot nicks", variable=self.check_bot_nicks_var).pack(side=tk.LEFT, padx=5)

        self.enable_notif_log_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Enable notification log", variable=self.enable_notif_log_var,
                       command=self.toggle_notif_log).pack(side=tk.LEFT, padx=5)

        self.notif_log_var = tk.StringVar()
        self.notif_log_entry = ttk.Entry(options_frame, textvariable=self.notif_log_var, width=30, state=tk.DISABLED)
        self.notif_log_entry.pack(side=tk.LEFT, padx=5)

        self.notif_log_button = ttk.Button(options_frame, text="Browse", command=self.browse_notif_log, state=tk.DISABLED)
        self.notif_log_button.pack(side=tk.LEFT)

        # === Control Section ===
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring, width=20)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_monitoring, state=tk.DISABLED, width=15)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Save Config", command=self.save_config, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Load Config", command=self.load_config, width=15).pack(side=tk.LEFT, padx=5)

        # Status
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(side=tk.LEFT, padx=20)

        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="● Stopped", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # === Log Viewer Section ===
        log_frame = ttk.LabelFrame(main_frame, text="Live Logs", padding="5")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        log_buttons = ttk.Frame(log_frame)
        log_buttons.grid(row=1, column=0, sticky=tk.W, pady=5)

        ttk.Button(log_buttons, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)

        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_buttons, text="Auto-scroll", variable=self.auto_scroll_var).pack(side=tk.LEFT, padx=5)

        # Start log update timer
        self.update_logs()

    def toggle_notif_log(self):
        if self.enable_notif_log_var.get():
            self.notif_log_entry.config(state=tk.NORMAL)
            self.notif_log_button.config(state=tk.NORMAL)
        else:
            self.notif_log_entry.config(state=tk.DISABLED)
            self.notif_log_button.config(state=tk.DISABLED)

    def browse_notif_log(self):
        filename = filedialog.asksaveasfilename(
            title="Select notification log file",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.notif_log_var.set(filename)

    def add_log_dir(self):
        directory = filedialog.askdirectory(title="Select IRC log directory")
        if directory and directory not in self.log_dirs:
            self.log_dirs.append(directory)
            self.log_dir_listbox.insert(tk.END, directory)

    def remove_log_dir(self):
        selection = self.log_dir_listbox.curselection()
        if selection:
            index = selection[0]
            self.log_dir_listbox.delete(index)
            del self.log_dirs[index]

    def validate_config(self):
        """Validate configuration before starting"""
        if not self.topic_var.get():
            messagebox.showerror("Configuration Error", "ntfy Topic is required")
            return False
        if not self.nick_var.get():
            messagebox.showerror("Configuration Error", "Your Nick is required")
            return False
        if not self.log_dirs:
            messagebox.showerror("Configuration Error", "At least one log directory is required")
            return False
        return True

    def start_monitoring(self):
        if not self.validate_config():
            return

        # Build command
        cmd = [sys.executable, "interview_notify.py"]
        cmd.extend(["--topic", self.topic_var.get()])
        cmd.extend(["--server", self.server_var.get()])
        cmd.extend(["--nick", self.nick_var.get()])
        cmd.extend(["--bot-nicks", self.bot_nicks_var.get()])
        cmd.extend(["--mode", self.mode_var.get()])
        cmd.extend(["--rate-limit", self.rate_limit_var.get()])

        for log_dir in self.log_dirs:
            cmd.extend(["--log-dir", log_dir])

        if not self.check_bot_nicks_var.get():
            cmd.append("--no-check-bot-nicks")

        if self.enable_notif_log_var.get() and self.notif_log_var.get():
            cmd.extend(["--notification-log", self.notif_log_var.get()])

        # Add verbosity
        cmd.extend(["-v", "-v", "-v"])

        try:
            self.log_message("Starting interview-notify with command:")
            self.log_message(" ".join(cmd))
            self.log_message("-" * 60)

            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Start thread to read output
            self.output_thread = threading.Thread(target=self.read_output, daemon=True)
            self.output_thread.start()

            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="● Running", foreground="green")

            self.log_message("Monitoring started successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
            self.log_message(f"ERROR: {e}")

    def stop_monitoring(self):
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="● Stopped", foreground="red")

            self.log_message("-" * 60)
            self.log_message("Monitoring stopped")

    def read_output(self):
        """Read process output in separate thread"""
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.log_queue.put(line.rstrip())
        except Exception as e:
            self.log_queue.put(f"ERROR reading output: {e}")

    def update_logs(self):
        """Update log display from queue"""
        try:
            while True:
                line = self.log_queue.get_nowait()
                self.log_message(line)
        except queue.Empty:
            pass

        # Check if process died unexpectedly
        if self.process and self.process.poll() is not None:
            self.log_message("Process terminated unexpectedly!")
            self.stop_monitoring()

        # Schedule next update
        self.root.after(100, self.update_logs)

    def log_message(self, message):
        """Add message to log viewer"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_logs(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def save_config(self):
        """Save configuration to file"""
        config = {
            "topic": self.topic_var.get(),
            "server": self.server_var.get(),
            "nick": self.nick_var.get(),
            "bot_nicks": self.bot_nicks_var.get(),
            "mode": self.mode_var.get(),
            "rate_limit": self.rate_limit_var.get(),
            "log_dirs": self.log_dirs,
            "check_bot_nicks": self.check_bot_nicks_var.get(),
            "enable_notif_log": self.enable_notif_log_var.get(),
            "notif_log": self.notif_log_var.get()
        }

        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", f"Configuration saved to {CONFIG_FILE}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def load_config(self):
        """Load configuration from file"""
        if not CONFIG_FILE.exists():
            return

        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)

            self.topic_var.set(config.get("topic", ""))
            self.server_var.set(config.get("server", "https://ntfy.sh/"))
            self.nick_var.set(config.get("nick", ""))
            self.bot_nicks_var.set(config.get("bot_nicks", "Gatekeeper"))
            self.mode_var.set(config.get("mode", "red"))
            self.rate_limit_var.set(config.get("rate_limit", "60"))
            self.check_bot_nicks_var.set(config.get("check_bot_nicks", True))
            self.enable_notif_log_var.set(config.get("enable_notif_log", False))
            self.notif_log_var.set(config.get("notif_log", ""))

            # Load log directories
            self.log_dirs = config.get("log_dirs", [])
            self.log_dir_listbox.delete(0, tk.END)
            for log_dir in self.log_dirs:
                self.log_dir_listbox.insert(tk.END, log_dir)

            self.toggle_notif_log()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")

    def on_closing(self):
        """Handle window closing"""
        if self.process:
            if messagebox.askokcancel("Quit", "Monitoring is running. Stop and quit?"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = InterviewNotifyGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
