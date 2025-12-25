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
        
        self._recording_seconds = 0
        self._timer_running = False
        self._timer_job = None

    def _set_window_icon(self):
        try:
            icon_path = self._resource_path("gui/assets/app.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon load failed: {e}")
    
    def _resource_path(self, relative_path: str) -> str:
        if getattr(sys, "frozen", False):
            # pyinstaller
            return str(Path(sys._MEIPASS) / relative_path)
        return str(Path(__file__).resolve().parent.parent / relative_path)
    
    def _update_timer(self):
        if self._timer_running:
            self._recording_seconds += 1
            self._display_timer()
            # вызываем себя через 1 сек
            self._timer_job = self.after(1000, self._update_timer)
    
    def _display_timer(self):
        minutes, seconds = divmod(self._recording_seconds, 60)
        time_str = f"Recording time: {minutes:02d}:{seconds:02d}"
        self.timer_label.config(text=time_str)

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
        
        self.timer_label = ttk.Label(main, text="Recording time: 00:00")
        self.timer_label.pack(anchor="w", pady=(0, 5))

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
        
        self._recording_seconds = 0
        self._timer_running = True
        self._update_timer()

        self.btn_record.state(["disabled"])
        self.btn_pause.state(["!disabled"])
        self.btn_stop.state(["!disabled"])

    def pause_recording(self):
        if not self.recorder:
            return

        if self.recorder._pause_event.is_set():
            self.recorder.pause()
            self._timer_running = False
            if self._timer_job:
                self.after_cancel(self._timer_job)
                self._timer_job = None
            self.btn_pause.config(text="▶ Resume")
        else:
            self.recorder.resume()
            self._timer_running = True
            self._update_timer()
            self.btn_pause.config(text="⏸ Pause")

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
        
        self._timer_running = False
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

        minutes, seconds = divmod(self._recording_seconds, 60)
        self.log_message(f"Final recording duration: {minutes:02d}:{seconds:02d}")
        self._recording_seconds = 0
        self._display_timer()

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
