"""
AEPGP Context Menu - Complete Installer/Uninstaller

This is the main entry point for the AEPGP Windows context menu installation.
It provides a GUI for installing or uninstalling the context menu integration.
"""

import sys
import os
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess


def is_admin():
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate_privileges():
    """Re-run with administrator privileges"""
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join([f'"{arg}"' for arg in sys.argv]),
            None,
            1
        )
        return True
    except:
        return False


class AEPGPInstallerGUI:
    """GUI for AEPGP Context Menu Installer"""

    def __init__(self, root):
        self.root = root
        self.root.title("AEPGP Context Menu Setup")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Center window
        self.center_window()

        # Create UI
        self.create_ui()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_ui(self):
        """Create the user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg="#0066cc", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="AEPGP Context Menu",
            font=("Segoe UI", 18, "bold"),
            bg="#0066cc",
            fg="white"
        )
        title_label.pack(pady=20)

        # Main content
        content_frame = tk.Frame(self.root, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Description
        desc_label = tk.Label(
            content_frame,
            text="Install or uninstall Windows Explorer context menu integration\n"
                 "for encrypting and decrypting files with your AEPGP card.",
            font=("Segoe UI", 10),
            justify=tk.LEFT,
            wraplength=450
        )
        desc_label.pack(pady=(0, 20))

        # Features
        features_frame = tk.LabelFrame(
            content_frame,
            text="Features",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=10
        )
        features_frame.pack(fill=tk.X, pady=(0, 20))

        features = [
            "✓ Right-click to encrypt any file",
            "✓ Right-click to decrypt .gpg/.pgp/.asc files",
            "✓ Automatic AmbiSecure token detection",
            "✓ Secure GnuPG integration"
        ]

        for feature in features:
            label = tk.Label(
                features_frame,
                text=feature,
                font=("Segoe UI", 9),
                justify=tk.LEFT
            )
            label.pack(anchor=tk.W, pady=2)

        # Status
        self.status_label = tk.Label(
            content_frame,
            text=self.get_installation_status(),
            font=("Segoe UI", 9, "italic"),
            fg="#666"
        )
        self.status_label.pack(pady=(0, 20))

        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X)

        self.install_btn = tk.Button(
            button_frame,
            text="Install",
            command=self.install,
            bg="#0066cc",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=30,
            pady=10,
            cursor="hand2"
        )
        self.install_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.uninstall_btn = tk.Button(
            button_frame,
            text="Uninstall",
            command=self.uninstall,
            bg="#cc3300",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=30,
            pady=10,
            cursor="hand2"
        )
        self.uninstall_btn.pack(side=tk.LEFT, padx=(0, 10))

        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=self.root.quit,
            font=("Segoe UI", 10),
            padx=30,
            pady=10,
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)

    def get_installation_status(self):
        """Check if context menu is currently installed"""
        try:
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\AEPGP.Encrypt")
                winreg.CloseKey(key)
                return "Status: Currently installed"
            except FileNotFoundError:
                return "Status: Not installed"
        except:
            return "Status: Unknown"

    def run_script(self, script_name):
        """Run a Python script and show output"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, script_name)

        if not os.path.exists(script_path):
            messagebox.showerror(
                "Error",
                f"Script not found: {script_name}\n\nPlease ensure all files are present."
            )
            return

        # Create progress window
        progress = tk.Toplevel(self.root)
        progress.title("Please wait...")
        progress.geometry("400x150")
        progress.resizable(False, False)
        progress.transient(self.root)
        progress.grab_set()

        # Center progress window
        progress.update_idletasks()
        x = (progress.winfo_screenwidth() // 2) - 200
        y = (progress.winfo_screenheight() // 2) - 75
        progress.geometry(f'400x150+{x}+{y}')

        label = tk.Label(
            progress,
            text=f"Running {script_name}...\nPlease wait.",
            font=("Segoe UI", 10),
            pady=20
        )
        label.pack()

        progressbar = ttk.Progressbar(progress, mode='indeterminate')
        progressbar.pack(fill=tk.X, padx=20, pady=20)
        progressbar.start()

        # Run script in background
        def run():
            try:
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )

                progress.destroy()

                if result.returncode == 0:
                    messagebox.showinfo(
                        "Success",
                        f"{script_name.replace('_', ' ').title()} completed successfully!"
                    )
                    # Update status
                    self.status_label.config(text=self.get_installation_status())
                else:
                    error_msg = result.stderr if result.stderr else result.stdout
                    messagebox.showerror(
                        "Error",
                        f"Operation failed:\n\n{error_msg}"
                    )
            except Exception as e:
                progress.destroy()
                messagebox.showerror(
                    "Error",
                    f"Failed to run script:\n\n{str(e)}"
                )

        # Run in thread to avoid blocking UI
        import threading
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def install(self):
        """Install the context menu"""
        if not is_admin():
            messagebox.showwarning(
                "Administrator Required",
                "Installation requires Administrator privileges.\n\n"
                "The program will now restart with elevated privileges."
            )
            if elevate_privileges():
                self.root.quit()
            return

        response = messagebox.askyesno(
            "Install AEPGP Context Menu",
            "This will install context menu entries for encrypting and decrypting files.\n\n"
            "Do you want to continue?"
        )

        if response:
            self.run_script("install_menu.py")

    def uninstall(self):
        """Uninstall the context menu"""
        if not is_admin():
            messagebox.showwarning(
                "Administrator Required",
                "Uninstallation requires Administrator privileges.\n\n"
                "The program will now restart with elevated privileges."
            )
            if elevate_privileges():
                self.root.quit()
            return

        response = messagebox.askyesno(
            "Uninstall AEPGP Context Menu",
            "This will remove AEPGP context menu entries from Windows Explorer.\n\n"
            "Do you want to continue?"
        )

        if response:
            self.run_script("uninstall_menu.py")


def main():
    """Main entry point"""
    if sys.platform != 'win32':
        print("This installer is only for Windows.")
        sys.exit(1)

    # Create GUI
    root = tk.Tk()
    app = AEPGPInstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
