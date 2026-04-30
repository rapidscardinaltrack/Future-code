# weather_diary.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary / Дневник погоды")
        self.root.geometry("800x600")
        
        # Список записей
        self.records = []
        self.filename = "weather_records.json"
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка сохраненных данных
        self.load_records()
        
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поля ввода
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", pady=2)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, sticky="w", pady=2)
        self.temperature_entry = ttk.Entry(input_frame, width=20)
        self.temperature_entry.grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Label(input_frame, text="Описание:").grid(row=2, column=0, sticky="w", pady=2)
        self.description_entry = ttk.Entry(input_frame, width=40)
        self.description_entry.grid(row=2, column=1, columnspan=2, sticky="w", pady=2)
        
        ttk.Label(input_frame, text="Осадки:").grid(row=3, column=0, sticky="w", pady=2)
        self.precipitation_var = tk.BooleanVar()
        self.precipitation_check = ttk.Checkbutton(input_frame, variable=self.precipitation_var)
        self.precipitation_check.grid(row=3, column=1, sticky="w", pady=2)
        
        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить запись", command=self.add_record)
        add_btn.grid(row=4, column=1, pady=10)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding="10")
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, sticky="w", pady=2)
        self.filter_date_entry = ttk.Entry(filter_frame, width=20)
        self.filter_date_entry.grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(filter_frame, text="Температура выше:").grid(row=1, column=0, sticky="w", pady=2)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=20)
        self.filter_temp_entry.grid(row=1, column=1, sticky="w", pady=2)
        
        filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_btn.grid(row=2, column=0, pady=5)
        
        reset_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        reset_filter_btn.grid(row=2, column=1, pady=5)
        
        # Таблица для отображения записей
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание Treeview с прокруткой
        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления внизу
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=5)
        
        save_btn = ttk.Button(bottom_frame, text="Сохранить в файл", command=self.save_records)
        save_btn.pack(side="left", padx=5)
        
        delete_btn = ttk.Button(bottom_frame, text="Удалить запись", command=self.delete_record)
        delete_btn.pack(side="left", padx=5)
        
        clear_btn = ttk.Button(bottom_frame, text="Очистить все", command=self.clear_all_records)
        clear_btn.pack(side="left", padx=5)
    
    def validate_record(self, date_str, temperature_str, description):
        """Проверка корректности ввода данных"""
        # Проверка даты
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return False
        
        # Проверка температуры
        try:
            float(temperature_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return False
        
        # Проверка описания
        if not description.strip():
            messagebox.showerror("Ошибка", "Описание не может быть пустым!")
            return False
        
        return True
    
    def add_record(self):
        """Добавление новой записи"""
        date_str = self.date_entry.get().strip()
        temperature_str = self.temperature_entry.get().strip()
        description = self.description_entry.get().strip()
        precipitation = self.precipitation_var.get()
        
        if self.validate_record(date_str, temperature_str, description):
            record = {
                "date": date_str,
                "temperature": float(temperature_str),
                "description": description,
                "precipitation": precipitation
            }
            
            self.records.append(record)
            self.update_table()
            self.clear_entries()
            messagebox.showinfo("Успех", "Запись добавлена!")
    
    def update_table(self, records=None):
        """Обновление таблицы с записями"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        display_records = records if records is not None else self.records
        
        for record in display_records:
            precipitation_text = "Да" if record["precipitation"] else "Нет"
            temp_text = f"{record['temperature']:.1f}°C" if isinstance(record['temperature'], (int, float)) else record['temperature']
            
            self.tree.insert("", "end", values=(
                record["date"],
                temp_text,
                record["description"],
                precipitation_text
            ))
    
    def apply_filter(self):
        """Применение фильтров к записям"""
        filtered_records = self.records.copy()
        
        # Фильтр по дате
        filter_date = self.filter_date_entry.get().strip()
        if filter_date:
            try:
                datetime.strptime(filter_date, "%d.%m.%Y")
                filtered_records = [r for r in filtered_records if r["date"] == filter_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты для фильтрации!")
                return
        
        # Фильтр по температуре
        filter_temp = self.filter_temp_entry.get().strip()
        if filter_temp:
            try:
                min_temp = float(filter_temp)
                filtered_records = [r for r in filtered_records if r["temperature"] > min_temp]
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную температуру для фильтрации!")
                return
        
        self.update_table(filtered_records)
    
    def reset_filter(self):
        """Сброс фильтрации"""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()
    
    def delete_record(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        # Получаем значения выбранной строки
        values = self.tree.item(selected[0])["values"]
        date = values[0]
        temp = float(values[1].replace("°C", ""))
        description = values[2]
        precipitation = values[3] == "Да"
        
        # Находим и удаляем запись
        self.records = [r for r in self.records 
                       if not (r["date"] == date and 
                              r["temperature"] == temp and 
                              r["description"] == description and 
                              r["precipitation"] == precipitation)]
        
        self.update_table()
        messagebox.showinfo("Успех", "Запись удалена!")
    
    def clear_all_records(self):
        """Очистка всех записей"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все записи?"):
            self.records.clear()
            self.update_table()
    
    def clear_entries(self):
        """Очистка полей ввода"""
        self.date_entry.delete(0, tk.END)
        self.temperature_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.precipitation_var.set(False)
    
    def save_records(self):
        """Сохранение записей в JSON файл"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(self.records, file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Записи сохранены в файл {self.filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def load_records(self):
        """Загрузка записей из JSON файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    self.records = json.load(file)
                self.update_table()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()

if __name__ == "__main__":
    main()