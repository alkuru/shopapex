@echo off
chcp 65001 >nul
title Загрузчик прайса АвтоКонтинента

echo.
echo ========================================
echo   Загрузчик прайса АвтоКонтинента
echo ========================================
echo.

echo Проверяем Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python с https://python.org
    pause
    exit /b 1
)

echo Проверяем зависимости...
python -c "import pandas, requests, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo Устанавливаем зависимости...
    pip install -r price_uploader_requirements.txt
    if errorlevel 1 (
        echo ОШИБКА: Не удалось установить зависимости!
        pause
        exit /b 1
    )
)

echo.
echo Запускаем программу...
echo.

python price_uploader_standalone.py

if errorlevel 1 (
    echo.
    echo ОШИБКА: Программа завершилась с ошибкой!
    pause
)

echo.
echo Программа завершена.
pause 