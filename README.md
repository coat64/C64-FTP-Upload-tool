# C64u FTP Upload Tool

A small, cross-platform GUI utility to upload files from a PC to a **Commodore 64 Ultimate** via FTP.

This tool is intended as a simple helper for quickly copying disk images and program files to the Ultimate’s internal storage over Wi-Fi.

---

## Features

- Select a local file using a standard file dialog
- Upload files to a chosen directory on the C64 Ultimate
- Automatically creates missing subdirectories on the C64
- Overwrite confirmation if the file already exists
- Remembers basic settings (IP address, target directory)
- Simple, no-nonsense user interface

---

## Requirements

- Commodore 64 Ultimate with Wi-Fi configured
- PC and C64 Ultimate connected to the same network
- Python 3.x (when running it with python)

---

## Setup on the C64 Ultimate  
*(assuming Wi-Fi is already configured – see Ultimate manual, page 147)*

1. Open the **Ultimate menu**
2. Go to **Network services & timezone**
3. Enable **FTP file service** and  save to flash
4. Go to **Wi-Fi network setup**
5. Enable **Use DHCP** and  save to flash
6. Power-cycle the C64 Ultimate (turn it off and on)  
   *(required to obtain or refresh the IP address)*
7. Return to **Wi-Fi network setup**
8. Note the **Active IP address**, second line from bottom 
    (for example: `192.168.123.234`)
---

## Using C64u_upload

1. Start the program on the PC (executable or python-script)
2. Select the file you want to upload to the C64u (for example: `.d64`, `.prg`, etc.)
3. **First use only**:  
   - Enter the **Active IP address of the C64 Ultimate**  
   - This address will be remembered after the first successful upload
4. Enter the **target directory** on the C64 Ultimate  
   - The **first part of the directory must already exist** on the C64  
     (for example: `Temp`, `SD`, `USB`, `Flash`, …)
   - Example:   **/SD**/MyFolder
   - If `MyFolder` does not exist, it will be created automatically
5. Press **Upload**
6. When the upload is finished, you can:
   - select another file to upload, or
   - close the program

---

## Troubleshooting

If an upload does not work:

- Is the C64 Ultimate powered on :)?
- Are **FTP** and **DHCP** enabled on the Ultimate?
- Is the **Active IP address** still correct?
- Does the first part of the target directory exist on the C64 Ultimate  
  (for example: `Temp`, `SD`, `USB`, `Flash`, …)?
- Are the PC and the C64 Ultimate connected to the same Wi-Fi network?
- Try rebooting the C64 Ultimate if problems persist

---

## Notes

- FTP access uses **plain FTP** (no username/password by default on the Ultimate)
- Directory paths must use forward slashes (`/`)
- The tool automatically switches to binary transfer mode

---

## License

Use it 🙂

---

Created by **Jan Albert Schenk**  and mostly ChatGPT 5.2  
January 2026
