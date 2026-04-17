import json
import datetime

# Этот скрипт — фундамент. 
# В будущем мы подключим сюда API ключи для реального поиска.
# Сейчас он генерирует актуальные "заглушки" на ближайшие даты, 
# чтобы ты увидел, как обновляется сайт.

def generate_data():
    today = datetime.date.today()
    
    # Имитация сбора данных от ИИ-агента
    events = [
        {
            "id": 1,
            "date": (today + datetime.timedelta(days=2)).isoformat(),
            "title": "FC Barcelona Match",
            "type": "foot",
            "desc": "Official match scheduled for this week."
        },
        {
            "id": 2,
            "date": (today + datetime.timedelta(days=5)).isoformat(),
            "title": "NAVI CS2 Tournament",
            "type": "navi",
            "desc": "Upcoming matches for NAVI."
        },
        {
            "id": 3,
            "date": (today + datetime.timedelta(days=10)).isoformat(),
            "title": "AAA Game Launch",
            "type": "game",
            "desc": "New anticipated game release."
        },
        {
            "id": 4,
            "date": (today + datetime.timedelta(days=1)).isoformat(),
            "title": "Co-op with Friends",
            "type": "game",
            "desc": "New trending game for group play."
        }
    ]
    
    # Сохраняем в JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=4)
    
    print("Data updated successfully!")

if __name__ == "__main__":
    generate_data()
