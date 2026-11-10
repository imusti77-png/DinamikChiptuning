@echo off
chcp 65001 >nul
py -m pip install PySide6 pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name "Dinamik Chiptuning" dinamik_chiptuning_pro.py
echo EXE dosyasi dist klasorunde.
pause
