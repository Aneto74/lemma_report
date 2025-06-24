import customtkinter as ctk
import threading
import os
from tkinter import filedialog, messagebox
import sys
import subprocess
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Список предлогов и союзов для исключения
PR = ("у", "от", "до", "из", "для", "без", "к", "по", "в", "на", "за",
      "через", "про", "с", "перед", "над", "о", "об", "во", "при", "и",
      "\n", "ли", "а", "не", "со", "н", "или")
SKIP5 = 5
EXPENSE = 0

class LemmaReportGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("CSV Lemma Report")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.center_window()
        self.setup_ui()
        self.in_path = ""
        self.lemmo_path = ""
        self.out_path = ""

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        title_label = ctk.CTkLabel(main_frame, text="CSV Lemma Report", font=ctk.CTkFont(size=32, weight="bold"))
        title_label.pack(pady=(20, 10))
        subtitle_label = ctk.CTkLabel(main_frame, text="Конвертер лемматизированных CSV файлов", font=ctk.CTkFont(size=16), text_color="gray")
        subtitle_label.pack(pady=(0, 30))
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", padx=20, pady=10)
        self.in_entry = ctk.CTkEntry(file_frame, placeholder_text="Выберите CSV из Мастера Отчётов", height=40, font=ctk.CTkFont(size=14))
        self.in_entry.pack(fill="x", padx=20, pady=(20, 5))
        in_btn = ctk.CTkButton(file_frame, text="Выбрать файл", command=self.select_in_file, width=180)
        in_btn.pack(padx=20, pady=(0, 10))
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        self.run_button = ctk.CTkButton(button_frame, text="Запустить обработку", command=self.start_processing, height=50, font=ctk.CTkFont(size=16, weight="bold"), fg_color="#1f538d", hover_color="#14375e")
        self.run_button.pack(side="left", expand=True, padx=(20, 20), pady=20)
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()
        self.status_label = ctk.CTkLabel(main_frame, text="Готов к работе", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.pack(pady=10)
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=10)
        preview_label = ctk.CTkLabel(preview_frame, text="Предварительный просмотр:", font=ctk.CTkFont(size=14, weight="bold"))
        preview_label.pack(anchor="w", padx=20, pady=(20, 10))
        self.preview_text = ctk.CTkTextbox(preview_frame, font=ctk.CTkFont(size=12), wrap="word")
        self.preview_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        info_label = ctk.CTkLabel(info_frame, text="ℹ️ Просто выберите CSV из Мастера Отчётов — всё остальное программа сделает сама!", font=ctk.CTkFont(size=12), text_color="gray")
        info_label.pack(pady=15)
        preview_btn = ctk.CTkButton(main_frame, text="Предварительный просмотр результата", command=self.preview_output, height=40, font=ctk.CTkFont(size=14), fg_color="#2d7d32", hover_color="#1b5e20")
        preview_btn.pack(padx=20, pady=(0, 10))

    def select_in_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            self.in_path = path
            self.in_entry.delete(0, "end")
            self.in_entry.insert(0, path)
            # Автоматически формируем имена для lemmo и out
            base, ext = os.path.splitext(path)
            self.lemmo_path = base + ".lemmo.csv"
            self.out_path = base + ".lemma_report.csv"

    def update_status(self, message, progress=None):
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)

    def start_processing(self):
        if not self.in_entry.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите исходный CSV файл")
            return
        self.run_button.configure(state="disabled")
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()

    def process_files(self):
        try:
            self.update_status("Запуск mystem...", 0.05)
            in_file = self.in_path
            lemmo_file = self.lemmo_path
            out_file = self.out_path
            if sys.platform == "win32":
                cmd = f'mystem.exe "{in_file}" "{lemmo_file}" -c -l'
            elif sys.platform == "darwin":
                cmd = f'./mystem "{in_file}" "{lemmo_file}" -c -l'
            else:
                cmd = None
            if cmd:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                _, err = proc.communicate()
                if err:
                    self.update_status(f"mystem: {err}", 0.1)
            else:
                self.update_status("mystem не поддерживается на этой платформе", 0)
                return
            # Проверяем, что файл лемм действительно появился
            if not os.path.exists(lemmo_file):
                time.sleep(0.5)
            if not os.path.exists(lemmo_file):
                self.update_status("Ошибка: mystem не создал файл лемм. Проверьте путь и наличие mystem.exe", 0)
                messagebox.showerror("Ошибка", f"mystem не создал файл лемм:\n{lemmo_file}")
                self.root.after(0, self.reset_ui)
                return
            self.update_status("Подсчет строк...", 0.15)
            try:
                with open(in_file, "r", encoding="utf-8") as f:
                    count = sum(1 for _ in f)
            except Exception as e:
                self.update_status(f"Ошибка чтения файла: {e}", 0)
                return
            self.update_status(f"Всего строк: {count}", 0.2)
            t = tstart = time.time()
            c = 0
            with open(out_file, "w", encoding="utf-8") as ho, \
                 open(in_file, "r", encoding="utf-8") as hf, \
                 open(lemmo_file, "r", encoding="utf-8") as hl:
                for s in hf:
                    c += 1
                    s = s.replace('"', '').replace('\n', '')
                    sl = hl.readline()
                    if c > SKIP5:
                        try:
                            a = s.split(';')
                            if len(a) < 7:
                                continue
                            if a[6] == "-":
                                a[6] = "0"
                            f = a[5].replace(",", ".")
                            if float(f) < EXPENSE:
                                continue
                            a_ = sl.split(';')
                            if not a_:
                                continue
                            a_[0] = a_[0].replace('"', '').replace('{', '').replace('}', '')
                            a2 = a_[0].split(' ')
                            for b in PR:
                                while b in a2:
                                    a2.remove(b)
                            for tmp in a2:
                                if tmp and tmp != " ":
                                    out = f"{tmp};{';'.join(a)}"
                                    ho.write(out + "\n")
                        except (IndexError, ValueError) as e:
                            continue
                    else:
                        out = s
                        if c == SKIP5:
                            out = f"Лемма;{out}"
                            ho.write(out + "\n")
                    if (time.time() - t) > 1:
                        t = time.time()
                        t2 = time.time() - tstart
                        c2 = int(count / c * t2 - t2) if c else 0
                        self.update_status(f"Обработано строк: {c}. Осталось примерно секунд: {c2}", min(0.2 + 0.8 * c / count, 1.0))
            self.update_status("Готово!", 1.0)
            messagebox.showinfo("Успех", f"Файл успешно сохранён: {os.path.basename(out_file)}")
            # Удаляем промежуточный файл
            try:
                if os.path.exists(lemmo_file):
                    os.remove(lemmo_file)
            except Exception as e:
                self.update_status(f"Не удалось удалить временный файл: {e}", 1.0)
        except Exception as e:
            self.update_status("Ошибка", 0)
            messagebox.showerror("Ошибка", str(e))
        finally:
            self.root.after(0, self.reset_ui)

    def preview_output(self):
        if not self.out_path or not os.path.exists(self.out_path):
            messagebox.showerror("Ошибка", "Сначала выполните обработку и дождитесь результата")
            return
        try:
            with open(self.out_path, "r", encoding="utf-8") as f:
                preview = ''.join([next(f) for _ in range(20)])
            self.preview_text.delete("0.0", "end")
            self.preview_text.insert("0.0", preview)
            self.update_status("Предпросмотр загружен", 1.0)
        except Exception as e:
            self.update_status("Ошибка", 0)
            messagebox.showerror("Ошибка", str(e))
        finally:
            self.root.after(0, self.reset_ui)

    def reset_ui(self):
        self.run_button.configure(state="normal")
        self.progress_bar.pack_forget()
        self.progress_bar.set(0)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LemmaReportGUI()
    app.run() 