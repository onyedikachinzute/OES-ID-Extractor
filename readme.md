# OES ID Card PDF-to-Requirement-Document Extractor

An automated, fully offline desktop application designed to streamline ID card production workflows. The application scans uploaded ID card PDF or image files, extracts personnel photos and signatures, automates background removal, sharpens the imagery, and exports high-quality files named after each individual.

---

## Key Features

- **Document Parsing:** Automatically scans multi-page PDF documents or single images for photos, names, and signatures.
- **Auto-Cropping & Alignment:** Intelligently isolates personnel portraits and corresponding signatures on detection.
- **Background Removal:** Fully offline background extraction from both human portraits and raw signature inputs.
- **Image Enhancement:** Automatically sharpens and clarifies extracted photos to fit production-grade specifications.
- **Automated Named Export:** Produces two cleanly formatted, named final files per person for seamless directory matching.
- **Fully Offline Execution:** Zero external API or cloud dependencies, maintaining strict privacy over corporate and personnel data.
- **Batch Processing:** Drop multiple files into the queue and monitor status with a native, responsive progress tracking interface.

---

## 🚀 For End Users: One-Click Executable Setup

If you have downloaded the pre-compiled version (`OES-ID-Extractor.exe`), no setup is required on your machine. 

### How to Run:
1. Ensure the executable sits inside its own dedicated home directory folder (e.g., `OES-Extractor/`).
2. Double-click **`OES-ID-Extractor.exe`**.
3. **First-Time Launch Only:** A native loading window will pop up to securely fetch the background removal model asset (`u2net.onnx`) directly from an official repository mirror over your network.
4. Once completed, your workspace directories (`models/`, `photo/`, and `signatures/`) will automatically initialize alongside your `.exe` file, and the primary application GUI will open.

---

## 🛠️ For Developers: Source Installation & Build Instructions

This codebase comes equipped with an autonomous automation pipeline designed to cleanly install a localized virtual environment, update project dependencies, and package a compressed, standalone application binary.

### Prerequisites
- **OS:** Windows 10 / 11
- **Python:** Version 3.10 or higher (Ensure Python is added to your system's environment variables / `PATH`).

### Step-by-Step Installation
1. Clone the repository to your local drive:
   ```bash
   git clone https://github.com
   cd your-repo-name
   ```
2. Double-click the **`build.bat`** script file.

### What the `build.bat` Script Automates:
- **Environment Isolation:** Checks for an active localized environment. If `.venv` is missing, it initializes it completely from scratch.
- **Dependency Ingestion:** Safely updates core package handlers and checks your local `requirements.txt` file to update all structural python libraries.
- **Conflict Management:** Automatically purges old/obsolete internal library backports (like standard `pathlib`) that conflict with compilers.
- **PyInstaller Binary Build:** Bundles your code assets, operational modules, configurations, and branding icons into a clean standalone payload inside the newly populated `dist/` workspace folder.
- **Directory Launch:** Automatically pops open the local Windows File Explorer window showcasing your freshly compiled production binary as soon as compilation ends.

---

## 📂 Project Workspace Layout

```text
OES-ID-Extractor/
│
├── .venv/                      # Managed Python Virtual Environment (Git-ignored)
├── assets/                     # Core aesthetic graphics, styling icons, and branding
├── core/                       # Core functional components (detector, cropper, remover, etc.)
├── gui/                        # Application interface architecture and components
├── models/                     # Deep-learning assets (u2net.onnx) (Self-generated / Git-ignored)
├── photo/                      # Output directory for extracted portrait assets (Self-generated)
├── signatures/                 # Output directory for extracted signature assets (Self-generated)
│
├── build.bat                   # Full lifecycle build automation controller script
├── download_model.py           # On-demand asset verification and streaming pipeline
├── main.py                     # Primary entry-point and thread orchestrator
├── requirements.txt            # System dependencies manifest
└── .gitignore                  # Production system rule manifest (Keeps repository clean)
```

---

## 📄 License & Ownership

**Author:** Onyedikachi Nzute  
Developed strictly in accordance with systemic software requirements specification frameworks for secure standalone document asset extraction. All rights reserved.
