import json
import datetime
import os

# Профессиональный скрипт обновления данных
# Этот "мозг" будет находить события и сохранять их для твоего сайта

def generate_data():
    try:
        print("Начинаю процесс сбора данных...")
        today = datetime.date.today()
        
        # В будущем здесь будет реальный поиск через API (футбол, CS2, игры)
        # Сейчас создаем актуальные события на ближайшие дни
        events = [
            {
                "id": 1,
                "date": (today + datetime.timedelta(days=0)).isoformat(),
                "title": "Запуск системы GamerHub",
                "type": "game",
                "desc": "Твой персональный хаб успешно настроен и работает!"
            },
            {
                "id": 2,
                "date": (today + datetime.timedelta(days=2)).isoformat(),
                "title": "Матч Барселоны (Ожидание)",
                "type": "foot",
                "desc": "Скрипт проверяет расписание Ла Лиги..."
            },
            {
                "id": 3,
                "date": (today + datetime.timedelta(days=5)).isoformat(),
                "title": "NAVI Tournament Check",
                "type": "navi",
                "desc": "Поиск ближайших матчей на HLTV..."
            },
            {
                "id": 4,
                "date": "2026-04-17",
                "title": "Релиз Pragmata",
                "type": "game",
                "desc": "Событие из твоего списка пожеланий."
            }
        ]
        
        # Путь к файлу
        file_path = 'data.json'
        
        # Сохраняем данные
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=4)
        
        if os.path.exists(file_path):
            print(f"Успех! Файл {file_path} успешно создан.")
        else:
            print("Ошибка: Файл не был создан по неизвестной причине.")

    except Exception as e:
        print(f"Критическая ошибка при работе скрипта: {e}")

if __name__ == "__main__":
    generate_data()
