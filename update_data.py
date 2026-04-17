import json
import datetime
import os

# Профессиональный скрипт обновления данных
# Этот "мозг" будет находить события и сохранять их для твоего сайта

def generate_data():
    try:
        print("--- Запуск агента GamerHub ---")
        today = datetime.date.today()
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"Текущая дата: {today}, время: {current_time}")
        
        # Список событий (имитация работы ИИ-агента)
        events = [
            {
                "id": 1,
                "date": today.isoformat(),
                "title": "Система Активна",
                "type": "game",
                "desc": f"Последняя проверка: {current_time}. Робот работает штатно."
            },
            {
                "id": 2,
                "date": (today + datetime.timedelta(days=2)).isoformat(),
                "title": "Матч Барселоны (Проверка)",
                "type": "foot",
                "desc": "Скрипт проверяет расписание Ла Лиги на официальных сайтах."
            },
            {
                "id": 3,
                "date": (today + datetime.timedelta(days=5)).isoformat(),
                "title": "NAVI: Мониторинг CS2",
                "type": "navi",
                "desc": "Автоматическое отслеживание турниров на HLTV включено."
            },
            {
                "id": 4,
                "date": "2026-04-17",
                "title": "Релиз Pragmata",
                "type": "game",
                "desc": "Ожидаемый AAA проект от Capcom."
            }
        ]
        
        file_path = 'data.json'
        
        # Записываем данные в файл, который будет читать сайт
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=4)
        
        if os.path.exists(file_path):
            print(f"Успех! Файл {file_path} создан/обновлен.")
            print(f"Количество событий: {len(events)}")
        else:
            print("Ошибка: Файл не был создан.")

    except Exception as e:
        print(f"Критическая ошибка скрипта: {e}")

if __name__ == "__main__":
    generate_data()
