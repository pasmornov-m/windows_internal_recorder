## Windows Internal Recorder

**Windows Internal Recorder** is a lightweight desktop application for **capturing internal system audio on Windows**. Unlike standard audio recorders, it records **any sound played by your computer** — including music, videos, games, and system notifications — directly, without using a microphone.

### Features

* Record all system audio in **high-quality WAV format**
* Pause and resume recording without losing elapsed time
* Real-time recording duration timer
* Easy-to-use GUI built with **Tkinter**
* Choose save location and file name for recordings
* Logs recording events for debugging and tracking

### Use Cases

* Recording music or streaming audio
* Capturing sounds from games or apps
* Creating tutorials or demos with system audio

---

## Project structure

```
windows_internal_recorder/
├── app/
│   ├── core/
│   │   └── system_recorder.py      # System audio recording logic
│   ├── gui/
|   |   ├── assets/
│   |   |   └── icon.ico            # Application icon
│   |   └── gui.py                  # Tkinter GUI application
|   └ __main__.py                   # Main entry point
├── dist/                           # Build output (after PyInstaller)
│   └── WindowsInternalRecorder.exe
├── pyproject.toml                  # Project metadata and dependencies
├── README.md
└── .gitignore
```

---

## Installation

Make sure you have **Python 3.10+** and **uv** installed.

Install project dependencies:

```bash
uv pip install -e .
```

---

## Running the application (Python)

Run the GUI application directly from source:

```bash
uv run python app/__main__.py
```

---

## Building a standalone `.exe` (Windows)

Build a single-file Windows executable using **PyInstaller**:

```bash
uv run pyinstaller --onefile --windowed --icon app/gui/assets/app.ico --name "WindowsInternalRecorder" app/__main__.py
```

---

## Build output

After a successful build, the executable will be available at:

```
dist/
└── WindowsInternalRecorder.exe
```

