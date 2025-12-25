import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import sys
from app.core.system_recorder import SystemAudioRecorder




class RecorderGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("System Audio Recorder")
        self.geometry("650x420")
        self.minsize(500, 350)
        
        self._set_window_icon()

        self.recorder = None
        self.recording_thread = None

        self._init_style()
        self._build_ui()
    
    def _set_window_icon(self):
        try:
            icon_path = self._resource_path("app/gui/assets/app.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon load failed: {e}")
    
    def _resource_path(self, relative_path: str) -> str:
        if getattr(sys, "frozen", False):
            # pyinstaller
            return str(Path(sys._MEIPASS) / relative_path)
        return str(Path(__file__).resolve().parent.parent / relative_path)

    # ---------- STYLE ----------

    def _init_style(self):
        style = ttk.Style(self)

        # используем нативную тему Windows
        try:
            style.theme_use("vista")
        except tk.TclError:
            style.theme_use(style.theme_names()[0])

        style.configure("TButton", padding=6)

    # ---------- UI ----------

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        # ---- controls ----
        controls = ttk.Frame(main)
        controls.pack(pady=5)

        self.btn_record = ttk.Button(
            controls, text="● Record", command=self.start_recording
        )
        self.btn_pause = ttk.Button(
            controls, text="⏸ Pause", command=self.pause_recording, state="disabled"
        )
        self.btn_stop = ttk.Button(
            controls, text="■ Stop", command=self.stop_recording, state="disabled"
        )

        self.btn_record.grid(row=0, column=0, padx=5)
        self.btn_pause.grid(row=0, column=1, padx=5)
        self.btn_stop.grid(row=0, column=2, padx=5)

        # ---- log label ----
        ttk.Label(main, text="Log output:").pack(anchor="w", pady=(10, 2))

        # ---- log window ----
        log_frame = ttk.Frame(main)
        log_frame.pack(fill="both", expand=True)

        self.log = tk.Text(
            log_frame,
            height=12,
            wrap="word",
            state="disabled"
        )
        scrollbar = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.log.yview
        )
        self.log.configure(yscrollcommand=scrollbar.set)

        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ---------- logging ----------

    def log_message(self, msg: str):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    # ---------- actions ----------

    def start_recording(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")],
            title="Save recording as"
        )
        if not filename:
            return

        try:
            self.recorder = SystemAudioRecorder(
                filename=filename,
                logger=self.log_message
            )
        except Exception as e:
            messagebox.showerror("Initialization error", str(e))
            return

        self.recording_thread = threading.Thread(
            target=self.recorder.start,
            daemon=True
        )
        self.recording_thread.start()

        self.btn_record.state(["disabled"])
        self.btn_pause.state(["!disabled"])
        self.btn_stop.state(["!disabled"])

    def pause_recording(self):
        if not self.recorder:
            return

        if self.recorder._pause_event.is_set():
            self.recorder.pause()
            self.btn_pause.config(text="▶ Resume")
        else:
            self.recorder.resume()
            self.btn_pause.config(text="⏸ Pause")

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()

        self.btn_record.state(["!disabled"])
        self.btn_pause.state(["disabled"])
        self.btn_pause.config(text="⏸ Pause")
        self.btn_stop.state(["disabled"])

    # ---------- shutdown ----------

    def on_close(self):
        if self.recorder:
            self.recorder.stop()
        self.destroy()


if __name__ == "__main__":
    app = RecorderGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
