#########################################################################
## C64u FTP Upload Tool version 1                                      ##
##                                                                     ##
## A  small cross-platform GUI utility to upload a selected local file ##
## to a Commodore 64 ultimate (or other compatible device) via FTP.    ##
##                                                                     ##
## Features:                                                           ##
##  - File selection via standard file dialog                          ##
##  - Upload to a target directory of your choice on the C64           ##
##  - Automatic creation of missing directories on the c64             ##
##  - Overwrite confirmation if the file already exists                ##
##  - Remembering user settings (host, user, target directory)         ##
##    stored in the per-user temporary folder on the pc                ##
##  - Simple and basic interface                                       ##
##                                                                     ##
##  If you want to add user and password, uncomment the lines          ##
##  with ## at the front en delete the sometimes replacing lines.      ##
##                                                                     ##
##  Jan Albert Schenk and mostly ChatGPT 5.2, Jan. 2026                ##
##  License: Use it :)                                                 ##
#########################################################################

import json
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ftplib import FTP, error_perm
from pathlib import Path


# ---------- Settings ----------
CONFIG_FILE = Path(tempfile.gettempdir()) / "C64u_ftp_upload_settings.json"

def load_settings() -> dict:
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}

def save_settings(data: dict) -> None:
    try:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# ---------- FTP helpers ----------
def ftp_connect(host: str, user: str = "", password: str = "", timeout: int = 10) -> FTP:
    ftp = FTP()
    ftp.connect(host, 21, timeout=timeout)
##    ftp.login(user=user, passwd=password)
    ftp.login()
    ftp.voidcmd("TYPE I")  # binary mode
    return ftp

def ensure_dir(ftp: FTP, remote_dir: str) -> None:
    parts = [p for p in remote_dir.strip("/").split("/") if p]
    is_abs = remote_dir.startswith("/")
    if is_abs:
        ftp.cwd("/")
    for part in parts:
        try:
            ftp.cwd(part)
        except error_perm:
            ftp.mkd(part)
            ftp.cwd(part)

def upload_file(host: str, local_path: str, remote_dir: str,
                user: str = "", password: str = "", overwrite: bool = False) -> None:
    local = Path(local_path)
    if not local.exists() or not local.is_file():
        raise FileNotFoundError(f"Local file not found: {local}")

    with ftp_connect(host, user, password) as ftp:
        ensure_dir(ftp, remote_dir)

        remote_name = local.name

        if not overwrite and remote_file_exists(ftp, remote_name):
            raise FileExistsError(remote_name)

        with local.open("rb") as f:
            ftp.storbinary(f"STOR {remote_name}", f)


def remote_file_exists(ftp: FTP, filename: str) -> bool:
    try:
        return filename in ftp.nlst()
    except error_perm:
        return False


# ---------- UI ----------
def main():
    root = tk.Tk()
    root.title("Upload selected file to the C64 (v1)")
    root.resizable(False, False)
    root.geometry("+100+100")

    state = {"local_file": "", "uploaded_ok": False}

    # Load stored settings (if any)
    stored = load_settings()

    defaults = {
        "host": stored.get("host", "192.168.xxx.xxx"),
##        "user": stored.get("user", ""),
##        "pass": "",                              #stored.get("pass", ""),
        "remote": stored.get("remote", "/Temp/NameFolder"),
    }


    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)

    entries = {}
    row = 0

    # --- Selected file ---
    file_var = tk.StringVar(value="Upload file: (none)")
    ttk.Label(frm, textvariable=file_var).grid(
        row=row, column=0, columnspan=2, sticky="w", pady=(0, 8)
    )
    row += 1

    # --- Target directory (prominent) ---
    ttk.Label(frm, text="To C64 directory").grid(
        row=row, column=0, sticky="e", padx=8, pady=6
    )
    e_remote = ttk.Entry(frm, width=40)
    e_remote.grid(row=row, column=1, sticky="w", padx=8, pady=6)
    e_remote.insert(0, defaults["remote"])
    entries["remote"] = e_remote
    row += 1

    # --- Buttons ---
    btns = ttk.Frame(frm)
    btns.grid(row=row, column=0, columnspan=2, pady=(12, 4))

    upload_btn = ttk.Button(btns, text="Upload")
    upload_btn.pack(side="left", padx=6)

    ttk.Button(btns, text="Stop", command=root.quit).pack(side="left", padx=6)
    row += 1

    # --- Status ---
    status = tk.StringVar(value="")
    ttk.Label(frm, textvariable=status).grid(
        row=row, column=0, columnspan=2, sticky="w", pady=(4, 8)
    )
    row += 1

    # --- Divider / Settings header ---
    ttk.Separator(frm, orient="horizontal").grid(
        row=row, column=0, columnspan=2, sticky="ew", pady=6
    )
    row += 1

    ttk.Separator(frm, orient="horizontal").grid(
        row=row, column=0, columnspan=2, sticky="ew", pady=6
    )
    row += 1

    ttk.Label(frm, text="Settings:").grid(
        row=row, column=0, columnspan=2, sticky="w", pady=(0, 4)
    )
    row += 1

    # --- Remaining settings ---
    settings = [
        ("C64-IP-address", "host"),
##        ("FTP-User (if needed)", "user"),
##        ("FTP-Password (if needed)", "pass"),
    ]

    for lab, key in settings:
        ttk.Label(frm, text=lab).grid(
            row=row, column=0, sticky="e", padx=8, pady=6
        )
        show = "*" if key == "pass" else ""
        e = ttk.Entry(frm, width=40, show=show)
        e.grid(row=row, column=1, sticky="w", padx=8, pady=6)
        e.insert(0, defaults[key])
        entries[key] = e
        row += 1

    def statusupd(text: str) -> None:
        status.set("")              # clear old text
        root.update_idletasks()      # force redraw
        status.set(text)

    def pick_file() -> bool:
        root.withdraw()
        path = filedialog.askopenfilename(
            parent=root,
            title="Select a file to upload to the C64",
            filetypes=[("All files", "*.*")]
        )
        root.deiconify()
        root.lift()
        root.focus_force()

        if not path:
            return False

        state["local_file"] = path
        file_var.set(f"Upload file: {path}")
        statusupd("Ready?")  #(f"Settings file: {CONFIG_FILE}")
        state["uploaded_ok"] = False
        upload_btn.config(text="Upload")

        return True

    def do_upload() -> None:
        host = entries["host"].get().strip()
##        user = entries["user"].get().strip()
##        pw = entries["pass"].get()
        user = ""
        pw = ""
        remote = entries["remote"].get().strip()
        remote = remote.replace("\\", "/")
        if not remote.startswith("/"):
            remote = "/" + remote
        captionanother = " Select another file to upload "
        if not state["local_file"]:
            statusupd("No file selected.")
            return
        if not host:
            statusupd("Host is empty.")
            return
        if not remote:
            statusupd("Remote directory is empty.")
            return

        try:
            statusupd("Uploading...")
            try:
                upload_file(host, state["local_file"], remote, user, pw)
            except FileExistsError as ex:
                answer = messagebox.askyesno(
                    "File already exists",
                    f"The file '{ex}' already exists on the C64.\n\nDo you want to overwrite it?",
                    parent=root
                )
                if not answer:
                    statusupd("Upload cancelled (already exists).")
                    state["uploaded_ok"] = True
                    upload_btn.config(text=captionanother)
                    return

                # retry with overwrite enabled
                upload_file(host, state["local_file"], remote, user, pw, overwrite=True)


            # Save after success
            save_settings({"host": host,
##                          "user": user,
##                           "pass": "",
                          "remote": remote})
            statusupd("Done!")
            state["uploaded_ok"] = True
            upload_btn.config(text=captionanother)
        except Exception as ex:
            statusupd(f"Error: {ex}")
            messagebox.showerror(
                "Upload failed",
                f"{ex}\n\n"
                "Troubleshooting:\n"
                "• Make sure FTP and DHCP are enabled on the Ultimate\n"
                "• Check if the IP address is (still) valid\n"
                "• Verify the C64 directory path, first part must exist on ultimate (SD,Temp, USB, etc.)\n"
                "• Check WiFi connection on both PC and C64\n"
                "• Try again or reboot the C64",
                parent=root
            )


    def on_upload_button():
        if state["uploaded_ok"]:
            if pick_file():
                return
            statusupd("File selection cancelled.")
            state["uploaded_ok"] = False
            upload_btn.config(text="Upload")
            return

        do_upload()



    upload_btn.config(command=on_upload_button)
    root.protocol("WM_DELETE_WINDOW", root.quit)

    if not pick_file():
        root.destroy()
        return

    entries["remote"].focus_set()
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    main()
