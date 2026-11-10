@echo off
chcp 65001 >nul
title Dinamik Chiptuning Kurulum
echo Gerekli kutuphaneler yukleniyor...
py -m pip install --upgrade pip
py -m pip install PySide6
echo.
echo Kurulum tamamlandi. Program baslatiliyor...
py "%~dp0dinamik_chiptuning_pro.py"
pause
