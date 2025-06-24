#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import subprocess
from typing import List, Tuple

# Конфигурация файлов
file = "./in.csv"
filelemmo = "./lemmo.csv"
codepage = "utf-8"
fileout = "./report_lemma_out.csv"
count = 0
skip5 = 5
# expense - фильтр по расходу
expense = 0

# Список предлогов и союзов для исключения
pr = ("у", "от", "до", "из", "для", "без", "к", "по", "в", "на", "за",
      "через", "про", "с", "перед", "над", "о", "об", "во", "при", "и",
      "\n", "ли", "а", "не", "со", "н", "или")

def run_mystem() -> None:
    """Запускает mystem для обработки файлов"""
    print(f"Производится обработка файла: {file}")
    print("Это займет пару минут.")
    
    try:
        if sys.platform == "win32":
            # надо прописать полный путь к EXE файлу
            # или поместить файл в основную директорию
            proc = subprocess.Popen(f"mystem.exe {file} {filelemmo} -c -l", 
                                  shell=True, stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, text=True)
            out, err = proc.communicate()
            if err:
                print(f"Предупреждение: {err}")
        elif sys.platform == "darwin":
            proc = subprocess.Popen(f"./mystem {file} {filelemmo} -c -l", 
                                  shell=True, stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, text=True)
            out, err = proc.communicate()
            if err:
                print(f"Предупреждение: {err}")
        else:
            print("Неподдерживаемая платформа")
            return
    except FileNotFoundError:
        print("Ошибка: mystem не найден. Убедитесь, что он установлен и доступен в PATH")
        return
    except Exception as e:
        print(f"Ошибка при запуске mystem: {e}")
        return

def count_lines() -> int:
    """Подсчитывает количество строк в файле"""
    print("Подсчет выполняемой работы.")
    count = 0
    try:
        with open(file, "r", encoding=codepage) as f:
            count = sum(1 for _ in f)
    except FileNotFoundError:
        print(f"Ошибка: файл {file} не найден")
        return 0
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return 0
    
    print(f"Всего строк: {count}")
    return count

def process_files() -> None:
    """Основная функция обработки файлов"""
    global count
    count = count_lines()
    if count == 0:
        return
    
    print("Начинаю обработку.")
    t = tstart = time.time()
    c = 0

    try:
        with open(fileout, "w", encoding=codepage) as ho, \
             open(file, "r", encoding=codepage) as hf, \
             open(filelemmo, "r", encoding=codepage) as hl:
            
            for s in hf:
                c += 1
                s = s.replace("\"", "").replace("\n", "")
                sl = hl.readline()
                
                if c > skip5:
                    try:
                        a = s.split(';')
                        
                        # Проверка на достаточное количество элементов
                        if len(a) < 7:
                            continue
                            
                        if a[6] == "-":
                            a[6] = "0"

                        f = a[5].replace(",", ".")

                        if float(f) < expense:
                            continue

                        # обработка lemmo файла
                        a_ = sl.split(';')
                        if not a_:
                            continue
                            
                        a_[0] = a_[0].replace("\"", "").replace("{", "").replace("}", "")
                        a2 = a_[0].split(' ')
                        
                        # Удаление предлогов и союзов
                        for b in pr:
                            while b in a2:
                                a2.remove(b)
                                
                        for tmp in a2:
                            if tmp and tmp != " ":
                                out = f"{tmp};{';'.join(a)}"
                                ho.write(out + "\n")
                    except (IndexError, ValueError) as e:
                        print(f"Ошибка при обработке строки {c}: {e}")
                        continue
                else:
                    out = s
                    if c == skip5:
                        out = f"Лемма;{out}"
                        ho.write(out + "\n")
                        
                # Прогресс обработки
                if (time.time() - t) > 1:
                    t = time.time()
                    t2 = time.time() - tstart
                    c2 = int(count / c * t2 - t2)
                    print(f"Обработано строк: {c}. Осталось примерно секунд: {c2}")
                    
    except FileNotFoundError as e:
        print(f"Ошибка: файл не найден - {e}")
    except Exception as e:
        print(f"Ошибка при обработке файлов: {e}")

def main() -> None:
    """Главная функция"""
    start_time = time.time()
    run_mystem()
    process_files()
    print(f"\nОбрабатывалось секунд: {int(time.time() - start_time)}")

if __name__ == "__main__":
    main()
