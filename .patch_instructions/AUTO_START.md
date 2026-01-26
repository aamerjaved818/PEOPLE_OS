# Auto-start backend at system startup (Windows)

These helpers let you register a Windows Scheduled Task that will start the PeopleOS backend automatically when the machine boots.

Files:

- `start_backend.ps1` — script that starts the backend using the workspace virtualenv python (or system `python` if venv missing).
- `install_autostart.ps1` — create the scheduled task (run as Administrator).
- `uninstall_autostart.ps1` — remove the scheduled task (run as Administrator).

Install (run as Administrator):

```powershell
# from project root
powershell -ExecutionPolicy Bypass -File .\.patch_instructions\install_autostart.ps1
```

Verify task created:

```powershell
schtasks /Query /TN "PeopleOS Backend" /V
```

Uninstall (run as Administrator):

```powershell
powershell -ExecutionPolicy Bypass -File .\.patch_instructions\uninstall_autostart.ps1
```

Notes & caveats:

- The scheduled task runs as SYSTEM by default when created with `/RL HIGHEST` and `ONSTART`. If you prefer to run under a specific user account, modify `install_autostart.ps1` to include credentials or use Task Scheduler UI.
- The script tries to use `.venv\Scripts\python.exe` inside the project root. If your environment differs, update `start_backend.ps1` with the correct Python executable.
- This will not start the frontend dev server (`npm run dev`). Starting the dev server at system startup is usually not desired for production systems.
- If you want the frontend started as well, I can add an optional script and task — tell me your preference.
