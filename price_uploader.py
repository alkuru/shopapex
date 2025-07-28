#!/usr/bin/env python3
"""
Программа для загрузки прайса АвтоКонтинента
Графический интерфейс с прогресс-баром
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import requests
import json
import threading
import time
import os
from datetime import datetime

class PriceUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Загрузчик прайса АвтоКонтинента")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Переменные
        self.file_path = tk.StringVar()
        self.progress_var = tk.IntVar()
        self.status_var = tk.StringVar(value="Готов к загрузке")
        self.is_uploading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Конфигурация сетки
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Загрузчик прайса АвтоКонтинента", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Выбор файла
        ttk.Label(main_frame, text="Excel файл:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.file_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Выбрать файл", command=self.select_file).grid(row=1, column=2, pady=5)
        
        # Настройки
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        settings_frame.columnconfigure(1, weight=1)
        
        self.clear_existing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Очистить существующие товары", 
                       variable=self.clear_existing_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.upload_button = ttk.Button(button_frame, text="Начать загрузку", 
                                       command=self.start_upload, style="Accent.TButton")
        self.upload_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Остановить", command=self.stop_upload).pack(side=tk.LEFT)
        
        # Прогресс
        progress_frame = ttk.LabelFrame(main_frame, text="Прогресс загрузки", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=1, column=0, pady=5)
        
        # Статус
        status_frame = ttk.LabelFrame(main_frame, text="Статус", padding="10")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                     wraplength=500)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Лог", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Конфигурация сетки для главного фрейма
        main_frame.rowconfigure(6, weight=1)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите Excel файл",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path.set(file_path)
            self.log(f"Выбран файл: {file_path}")
            
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_upload(self):
        if not self.file_path.get():
            messagebox.showerror("Ошибка", "Выберите файл для загрузки")
            return
            
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("Ошибка", "Файл не найден")
            return
            
        self.is_uploading = True
        self.upload_button.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Начинаем загрузку...")
        
        # Запускаем загрузку в отдельном потоке
        upload_thread = threading.Thread(target=self.upload_file)
        upload_thread.daemon = True
        upload_thread.start()
        
    def stop_upload(self):
        self.is_uploading = False
        self.status_var.set("Остановка загрузки...")
        self.log("Загрузка остановлена пользователем")
        
    def upload_file(self):
        try:
            file_path = self.file_path.get()
            self.log(f"Начинаем загрузку файла: {file_path}")
            
            # Читаем Excel файл
            self.log("Читаем Excel файл...")
            self.status_var.set("Читаем Excel файл...")
            
            df = pd.read_excel(file_path)
            total_rows = len(df)
            self.log(f"Найдено {total_rows} строк в файле")
            
            # Подключаемся к базе данных через API
            api_url = "http://localhost:8000/api/upload-price/"
            
            # Подготавливаем данные
            upload_data = {
                'file_path': file_path,
                'clear_existing': self.clear_existing_var.get(),
                'total_rows': total_rows
            }
            
            self.log("Отправляем данные на сервер...")
            self.status_var.set("Отправляем данные на сервер...")
            
            # Отправляем запрос на загрузку
            response = requests.post(api_url, json=upload_data, timeout=30)
            
            if response.status_code == 200:
                self.log("Загрузка начата на сервере")
                self.status_var.set("Загрузка начата на сервере")
                
                # Мониторим прогресс
                self.monitor_progress()
            else:
                self.log(f"Ошибка сервера: {response.status_code}")
                self.status_var.set(f"Ошибка сервера: {response.status_code}")
                
        except Exception as e:
            self.log(f"Ошибка: {str(e)}")
            self.status_var.set(f"Ошибка: {str(e)}")
        finally:
            self.is_uploading = False
            self.upload_button.config(state="normal")
            
    def monitor_progress(self):
        """Мониторинг прогресса загрузки"""
        try:
            while self.is_uploading:
                # Получаем прогресс с сервера
                progress_url = "http://localhost:8000/api/upload-progress/"
                response = requests.get(progress_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    progress = data.get('progress', 0)
                    created = data.get('created', 0)
                    updated = data.get('updated', 0)
                    
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"{progress}%")
                    
                    status_text = f"Прогресс: {progress}% | Создано: {created} | Обновлено: {updated}"
                    self.status_var.set(status_text)
                    
                    if progress >= 100:
                        self.log("Загрузка завершена!")
                        self.status_var.set("Загрузка завершена успешно!")
                        break
                        
                time.sleep(1)
                
        except Exception as e:
            self.log(f"Ошибка мониторинга: {str(e)}")
            self.status_var.set(f"Ошибка мониторинга: {str(e)}")

def main():
    root = tk.Tk()
    app = PriceUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main() 