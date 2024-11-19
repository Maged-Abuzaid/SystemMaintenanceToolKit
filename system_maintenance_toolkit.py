import ctypes
import errno
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import logging
from pathlib import Path
import queue


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("")
    return os.path.join(base_path, relative_path)


# Define section labels and their corresponding log file names
SECTION_LOG_FILES = {
    "System Health Check": "system_health_check.log",
    "Disk Cleanup": "disk_cleanup.log",
    "Defragment and Optimize Drives": "defragment.log"
}

# Define per-command loggers within System Health Check
COMMAND_LOG_FILES = {
    "checkhealth": "checkhealth.log",
    "scanhealth": "scanhealth.log",
    "Restorehealth": "Restorehealth.log",
    "sfc_scannow": "sfc_scannow.log",
    "AnalyzeComponentStore": "AnalyzeComponentStore.log",
    "StartComponentCleanup": "StartComponentCleanup.log"
}

# Define log directory before initializing loggers
LOG_DIR = resource_path('logs')
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name, log_file, level=logging.INFO):
    """
    Creates and returns a logger with a FileHandler.

    Args:
        name (str): Name of the logger.
        log_file (str): Name of the log file.
        level (int): Logging level.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers to the same logger
    if not logger.handlers:
        fh = logging.FileHandler(os.path.join(LOG_DIR, log_file), encoding='utf-8')
        fh.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        logger.addHandler(fh)

    return logger


def is_admin():
    """
    Check if the script is running with administrative privileges.
    Returns:
        bool: True if running as admin, False otherwise.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logging.error(f"Admin check failed: {e}")
        return False


class SystemMaintenanceToolkit:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap(resource_path('assets/icon.ico'))
        self.root.title("System Maintenance Toolkit")
        self.root.geometry("800x465")  # Increased height
        self.root.resizable(True, True)  # Made resizable

        # Configure main window's grid
        self.root.columnconfigure(0, weight=1)
        for i in range(5):  # Assuming 5 rows
            self.root.rowconfigure(i, weight=1)

        # Initialize a queue for thread-safe GUI updates
        self.gui_queue = queue.Queue()
        self.root.after(100, self.process_gui_queue)

        # Create a separate frame for the Clear All Logs button
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        clear_all_logs_button = ttk.Button(
            button_frame,
            text="Clear Logs",
            command=self.clear_all_logs,
            width=15
        )
        clear_all_logs_button.pack()

        # Initialize loggers
        self.initialize_loggers()

        # Create sections starting from row=1
        self.create_section("System Health Check", self.start_health_check, 1, button_label="Start")
        self.create_section("Disk Cleanup", self.disk_cleanup, 2, button_label="Clean")
        self.create_section("Defragment and Optimize Drives", self.defragment_drives, 3, button_label="Optimize")

    def initialize_loggers(self):
        """
        Initialize all loggers and store references for later use.
        """
        self.loggers = {}

        # Initialize section loggers
        for section, log_file in SECTION_LOG_FILES.items():
            if section == "Defragment and Optimize Drives":
                logger_name = "defragment"
            else:
                logger_name = section.lower().replace(' ', '_')
            self.loggers[logger_name] = get_logger(logger_name, log_file)
            print(f"Initialized logger: {logger_name}")  # Debug statement

        # Initialize per-command loggers
        for command, log_file in COMMAND_LOG_FILES.items():
            logger_name = command.lower().replace('/', '_')  # e.g., 'sfc_scannow'
            self.loggers[logger_name] = get_logger(logger_name, log_file)
            print(f"Initialized logger: {logger_name}")  # Debug statement

        # Initialize a separate error logger
        self.loggers['error_logger'] = get_logger('error_logger', 'error.log')
        print("Initialized error_logger")  # Debug statement

    def clear_all_logs(self):
        """
        Deletes all log files in the LOG_DIR after closing their handlers.
        """
        # Step 1: Close and remove all FileHandlers
        for logger_name, logger in self.loggers.items():
            handlers_to_remove = []
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    handlers_to_remove.append(handler)
            for handler in handlers_to_remove:
                logger.removeHandler(handler)
                self.loggers['error_logger'].debug(f"Removed handler {handler} from logger '{logger_name}'")

        # Step 2: Delete all log files
        for log_file in os.listdir(LOG_DIR):
            file_path = os.path.join(LOG_DIR, log_file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    # Use the 'error_logger' to log this action since others are detached
                    self.loggers['error_logger'].info(f"Cleared log file: {log_file}")
            except Exception as e:
                self.loggers['error_logger'].error(f"Error clearing log file {log_file}: {e}")

        # Step 3: Reinitialize the loggers
        self.initialize_loggers()

        # Inform the user
        messagebox.showinfo("Logs Cleared", "All log files have been cleared.")

    def process_gui_queue(self):
        while not self.gui_queue.empty():
            func, args = self.gui_queue.get()
            func(*args)
        self.root.after(100, self.process_gui_queue)

    def thread_safe_update_info_panel(self, panel, message):
        self.gui_queue.put((self.update_info_panel, (panel, message)))

    def update_info_panel(self, panel, message):
        panel.config(state='normal')
        panel.insert(tk.END, message + '\n\n')  # Added an extra newline for spacing
        panel.config(state='disabled')
        panel.see(tk.END)

    def reset_progress_bar_with_delay(self, progress_bar, delay=1000):
        """
        Resets the given progress bar after a specified delay.

        Args:
            progress_bar (ttk.Progressbar): The progress bar to reset.
            delay (int): Delay in milliseconds before resetting the progress bar.
        """
        self.root.after(delay, lambda: progress_bar.config(value=0))

    def create_section(self, label, command, row, button_label="Run"):
        frame = ttk.LabelFrame(self.root, text=label)
        frame.grid(row=row, column=0, padx=10, pady=5, sticky='ew')

        button = ttk.Button(
            frame,
            text=button_label,
            command=lambda: threading.Thread(target=command).start(),
            width=15
        )
        button.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        see_log_button = ttk.Button(
            frame,
            text="See Log",
            command=lambda: self.open_log(label),
            width=15
        )
        see_log_button.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        # Centering the buttons
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        progress = ttk.Progressbar(
            frame,
            orient="horizontal",
            length=300,
            mode='determinate'
        )
        progress.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='w')

        info_panel = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            height=6,
            width=54
        )
        info_panel.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky='w')
        info_panel.config(state='disabled')

        setattr(self, f'{label.lower().replace(" ", "_")}_progress', progress)
        setattr(self, f'{label.lower().replace(" ", "_")}_info', info_panel)

    def open_log(self, label):
        # Check if the label has a corresponding log file
        log_file = SECTION_LOG_FILES.get(label, None)

        if not log_file:
            messagebox.showwarning("Log Not Found", f"No log file mapping found for {label}.")
            return

        # Initialize the log window with tabs if label is "System Health Check"
        if label == "System Health Check":
            log_window = tk.Toplevel(self.root)
            log_window.title(f"{label} Log")
            log_window.geometry("700x500")

            # Create a notebook widget for tabs
            notebook = ttk.Notebook(log_window)
            notebook.pack(expand=True, fill='both')

            # Since "System Health Check" may have multiple commands, list them
            for command_name, log_file_name in COMMAND_LOG_FILES.items():
                # Create a new frame for each tab
                frame = ttk.Frame(notebook)
                tab_display_name = command_name.replace('_', ' ').capitalize()
                notebook.add(frame, text=tab_display_name)  # Set the tab name

                # Scrolled text widget to display log content
                log_text = scrolledtext.ScrolledText(
                    frame,
                    wrap=tk.WORD,
                    width=80,
                    height=20
                )
                log_text.pack(expand=True, fill='both')

                # Determine the full path of the log file
                log_file_path = os.path.join(LOG_DIR, log_file_name)

                # Check if log file exists and read content
                if os.path.exists(log_file_path):
                    try:
                        with open(log_file_path, 'r', encoding='utf-8') as file:
                            log_content = file.read()
                            log_text.insert(tk.END, log_content)
                    except Exception as e:
                        log_text.insert(tk.END, f"Error reading log file: {e}")
                else:
                    log_text.insert(tk.END, f"No log file found for {command_name}.")

                # Disable editing of the log content
                log_text.config(state='disabled')
        else:
            # For other sections, open a single log file
            log_file_path = os.path.join(LOG_DIR, log_file)

            if os.path.exists(log_file_path):
                try:
                    with open(log_file_path, 'r', encoding='utf-8') as file:
                        log_content = file.read()

                    # Create a new window for single log view
                    log_window = tk.Toplevel(self.root)
                    log_window.title(f"{label} Log")
                    log_window.geometry("600x400")

                    # Scrolled text widget for single log content
                    log_text = scrolledtext.ScrolledText(
                        log_window,
                        wrap=tk.WORD,
                        width=70,
                        height=20
                    )
                    log_text.pack(padx=10, pady=10)
                    log_text.insert(tk.END, log_content)
                    log_text.config(state='disabled')

                    # Clear button if not the System Health Check logs
                    if label != "System Health Check":
                        clear_log_button = ttk.Button(
                            log_window,
                            text="Clear Log",
                            command=lambda: self.clear_log_content(label)
                        )
                        clear_log_button.pack(pady=5)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open log file: {e}")
            else:
                # Show warning if the log file does not exist
                messagebox.showwarning("Log Not Found", f"No log file found for {label}.")

    def clear_log_content(self, label):
        log_file = SECTION_LOG_FILES.get(label, None)

        if not log_file:
            messagebox.showwarning("Log Not Found", f"No log file mapping found for {label}.")
            return

        log_file_path = os.path.join(LOG_DIR, log_file)

        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, 'w', encoding='utf-8') as file:
                    file.write("")
                messagebox.showinfo("Log Cleared", f"Log file for {label} has been cleared.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear log file: {e}")
        else:
            messagebox.showwarning("Log Not Found", f"No log file found for {label}.")

    def clear_info_panel(self, panel):
        panel.config(state='normal')
        panel.delete(1.0, tk.END)
        panel.config(state='disabled')

    def defragment_drives(self):
        # Use the pre-initialized defragment logger
        try:
            logger = self.loggers['defragment']
        except KeyError:
            messagebox.showerror("Logger Error", "Defragment logger not found.")
            return

        info_panel = self.defragment_and_optimize_drives_info
        self.clear_info_panel(info_panel)
        self.thread_safe_update_info_panel(info_panel, "Initialized Defragment and Optimize Drives")

        drives = ["C:", "D:"]  # Modify as needed
        progress = self.defragment_and_optimize_drives_progress
        progress["maximum"] = len(drives) * 100  # Assume 100 steps per drive as an approximation

        logger.info("Starting Defragmentation and Optimization")

        for i, drive in enumerate(drives):
            try:
                command = f"defrag {drive} /OPTIMIZE"
                proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True,
                    bufsize=1  # Line-buffered
                )
                steps = 100
                for step in range(steps):
                    if proc.poll() is not None:
                        break
                    time.sleep(0.1)  # Simulating processing time for each step
                    progress["value"] = (i * 100) + (step + 1)
                    message = f"Defragmenting {drive}: Step {step + 1}/{steps}"
                    self.thread_safe_update_info_panel(info_panel, message)
                    logger.info(message)
                    self.root.update_idletasks()
                stdout, stderr = proc.communicate()
                if proc.returncode == 0:
                    success_message = f"Optimized drive: {drive}"
                    self.thread_safe_update_info_panel(info_panel, success_message)
                    logger.info(success_message)
                else:
                    error_message = f"Failed to optimize drive {drive}: {stderr}"
                    self.thread_safe_update_info_panel(info_panel, error_message)
                    logger.error(error_message)
            except subprocess.CalledProcessError as e:
                error_message = f"Failed to optimize drive {drive}: {e}"
                self.thread_safe_update_info_panel(info_panel, error_message)
                logger.error(error_message)

        # Log completion message
        logger.info("Defragmentation and Optimization Completed")

        completion_message = "Defragmentation and optimization completed."
        self.thread_safe_update_info_panel(info_panel, completion_message)

        # Set progress to maximum
        progress["value"] = 100
        self.root.update_idletasks()

        # Schedule progress bar reset after 1 second (1000 milliseconds)
        self.gui_queue.put((self.reset_progress_bar_with_delay, (progress, 1000)))

    def ensure_admin(self):
        """
        Ensure the function has admin rights before proceeding.
        Exits the function if admin rights are not detected.
        """
        if not is_admin():
            self.loggers['error_logger'].error("Admin privileges are required to perform this operation.")
            message = (
                "Admin privileges are required to perform this operation.\n"
                "Please restart the program as an administrator."
            )
            self.thread_safe_update_info_panel(
                self.system_health_check_info,
                message
            )
            return False
        return True

    def disk_cleanup(self):
        # Ensure admin rights before proceeding with cleanup
        if not self.ensure_admin():
            return

        # Directories and files to target for cleanup
        cleanup_paths = [
            os.getenv('TEMP'),
            os.path.expanduser('~\\AppData\\Local\\Temp'),
            # [Other paths...]
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\History')
        ]

        # Use the pre-initialized disk cleanup logger
        logger = self.loggers['disk_cleanup']

        deleted_files = []
        in_use_files = []
        permission_denied_files = []

        self.clear_info_panel(self.disk_cleanup_info)
        self.thread_safe_update_info_panel(self.disk_cleanup_info, "Starting Disk Cleanup...\n")

        for path in cleanup_paths:
            if path and os.path.exists(path):
                for root_dir, dirs, files in os.walk(path, topdown=False):
                    for name in files:
                        file_path = Path(root_dir) / name
                        try:
                            file_path.unlink()
                            deleted_files.append(str(file_path))
                            logger.info(f"Deleted file: {file_path}")
                        except PermissionError as e:
                            if e.errno == errno.EACCES and getattr(e, 'winerror', 0) == 32:
                                in_use_files.append(str(file_path))
                                self.thread_safe_update_info_panel(
                                    self.disk_cleanup_info,
                                    f"In use by another program: {file_path}\n"
                                )
                                logger.warning(f"In use by another program: {file_path}")
                            else:
                                permission_denied_files.append(str(file_path))
                                self.thread_safe_update_info_panel(
                                    self.disk_cleanup_info,
                                    f"Permission denied for {file_path}\n"
                                )
                                logger.error(f"Permission denied for {file_path}")
                        except OSError as e:
                            self.thread_safe_update_info_panel(
                                self.disk_cleanup_info,
                                f"Error deleting {file_path}: {e}\n"
                            )
                            logger.error(f"Error deleting {file_path}: {e}")
                    for name in dirs:
                        dir_path = Path(root_dir) / name
                        try:
                            dir_path.rmdir()
                            deleted_files.append(str(dir_path))
                            logger.info(f"Deleted directory: {dir_path}")
                        except PermissionError as e:
                            if e.errno == errno.EACCES and getattr(e, 'winerror', 0) == 32:
                                in_use_files.append(str(dir_path))
                                self.thread_safe_update_info_panel(
                                    self.disk_cleanup_info,
                                    f"In use by another program: {dir_path}\n"
                                )
                                logger.warning(f"In use by another program: {dir_path}")
                            else:
                                permission_denied_files.append(str(dir_path))
                                self.thread_safe_update_info_panel(
                                    self.disk_cleanup_info,
                                    f"Permission denied for {dir_path}\n"
                                )
                                logger.error(f"Permission denied for {dir_path}")
                        except OSError as e:
                            self.thread_safe_update_info_panel(
                                self.disk_cleanup_info,
                                f"Error deleting {dir_path}: {e}\n"
                            )
                            logger.error(f"Error deleting {dir_path}: {e}")
            else:
                self.thread_safe_update_info_panel(
                    self.disk_cleanup_info,
                    f"Path not found or invalid: {path}\n"
                )
                logger.warning(f"Path not found or invalid: {path}")

        # Log completion message
        logger.info("Disk Cleanup Completed")
        logger.info(f"Deleted Files: {len(deleted_files)}")
        logger.info(f"In Use Files: {len(in_use_files)}")
        logger.info(f"Permission Denied Files: {len(permission_denied_files)}")

        completion_message = (
            "Disk cleanup completed\n"
            f"Deleted: {len(deleted_files)}\n"
            f"In Use: {len(in_use_files)}\n"
            f"Permission Denied: {len(permission_denied_files)}"
        )
        self.thread_safe_update_info_panel(self.disk_cleanup_info, completion_message)

        # Set progress to maximum
        progress = self.disk_cleanup_progress
        progress["value"] = 100
        self.root.update_idletasks()

        # Schedule progress bar reset after 1 second (1000 milliseconds)
        self.gui_queue.put((self.reset_progress_bar_with_delay, (progress, 1000)))

    def start_health_check(self):
        if not self.ensure_admin():
            return

        # Define commands and corresponding log file names
        commands = {
            "checkhealth": "Dism.exe /online /Cleanup-Image /checkhealth",
            "scanhealth": "Dism.exe /online /Cleanup-Image /scanhealth",
            "Restorehealth": "Dism.exe /online /Cleanup-Image /Restorehealth",
            "sfc_scannow": "sfc /scannow",
            "AnalyzeComponentStore": "Dism.exe /Online /Cleanup-Image /AnalyzeComponentStore",
            "StartComponentCleanup": "Dism.exe /Online /Cleanup-Image /StartComponentCleanup"
        }

        # Loggers for each command using self.loggers
        loggers = {
            "checkhealth": self.loggers['checkhealth'],
            "scanhealth": self.loggers['scanhealth'],
            "Restorehealth": self.loggers['restorehealth'],
            "sfc_scannow": self.loggers['sfc_scannow'],
            "AnalyzeComponentStore": self.loggers['analyzeComponentStore'],
            "StartComponentCleanup": self.loggers['StartComponentCleanup']
        }

        progress_increment = 100 / len(commands)
        progress = self.system_health_check_progress

        # Clear and initialize the info panel
        self.clear_info_panel(self.system_health_check_info)
        self.thread_safe_update_info_panel(
            self.system_health_check_info,
            "Initializing System Health Check..."
        )

        # Execute each command in sequence and log output
        for i, (command_name, command) in enumerate(commands.items(), start=1):
            # Display command start in info panel
            self.thread_safe_update_info_panel(
                self.system_health_check_info,
                f"Executing command {i}/{len(commands)}: {command}"
            )
            # Get the appropriate logger
            logger = loggers.get(command_name, self.loggers['error_logger'])

            try:
                # Execute the command and capture all output
                process = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=3600  # Adjust timeout as needed
                )

                # Log the entire output
                if process.stdout:
                    for line in process.stdout.splitlines():
                        logger.info(line.strip())

                # Check for command success or failure
                if process.returncode == 0:
                    success_message = f"Command {i} completed successfully."
                    self.thread_safe_update_info_panel(
                        self.system_health_check_info,
                        success_message
                    )
                    logger.info(success_message)
                else:
                    error_message = f"Command {i} failed with error code: {process.returncode}"
                    self.thread_safe_update_info_panel(
                        self.system_health_check_info,
                        error_message
                    )
                    logger.error(error_message)

            except subprocess.TimeoutExpired:
                error_message = f"Command {i} timed out."
                self.thread_safe_update_info_panel(
                    self.system_health_check_info,
                    error_message
                )
                logger.error(error_message)
                break  # Stop execution if a timeout occurs
            except Exception as e:
                error_message = f"Error executing command {i}: {e}"
                self.thread_safe_update_info_panel(
                    self.system_health_check_info,
                    error_message
                )
                logger.error(error_message)
                break  # Stop execution if an error occurs

            finally:
                # Update progress for each command completed
                progress["value"] += progress_increment
                self.root.update_idletasks()

        # Completion message after all commands
        self.thread_safe_update_info_panel(
            self.system_health_check_info,
            "System Health Check completed."
        )
        # Set progress to maximum
        progress["value"] = 100
        self.root.update_idletasks()

        # Schedule progress bar reset after 1 second (1000 milliseconds)
        self.gui_queue.put((self.reset_progress_bar_with_delay, (progress, 1000)))

    def ensure_admin(self):
        """
        Ensure the function has admin rights before proceeding.
        Exits the function if admin rights are not detected.
        """
        if not is_admin():
            self.loggers['error_logger'].error("Admin privileges are required to perform this operation.")
            message = (
                "Admin privileges are required to perform this operation.\n"
                "Please restart the program as an administrator."
            )
            self.thread_safe_update_info_panel(
                self.system_health_check_info,
                message
            )
            return False
        return True


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMaintenanceToolkit(root)
    root.mainloop()
