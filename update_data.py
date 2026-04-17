import json
import datetime
import os
import requests

# Этот скрипт — сердце автоматизации. 
# Он ищет игры NAVI, матчи Барселоны и релизы игр.

def fetch_navi_matches():
    """Имитация получения данных о матчах NAVI.
    В будущем здесь будет полноценный парсер HLTV или API Pandascore."""
    today = datetime.date.today()
    # Пример: NAVI часто играют на крупных турнирах. 
    # Добавим игру, которая "проходит сегодня" для теста.
    return [
        {
            "id": "navi_1",
            "date": today.isoformat(),
            "title": "NAVI vs FaZe Clan",
            "type": "navi",
            "desc": "PGL Major 2026 - Elimination Stage. Начало в 19:00."
        },
        {
            "id": "navi_2",
            "date": (today + datetime.timedelta(days=1)).isoformat(),
            "title": "NAVI vs Spirit (TBD)",
            "type": "navi",
            "desc": "Возможный матч плей-офф. Следим за результатами."
        }
    ]

def fetch_football_matches():
    """Данные о Барселоне и сборной Украины."""
    today = datetime.date.today()
    return [
        {
            "id": "barca_1",
            "date": (today + datetime.timedelta(days=2)).isoformat(),
            "title": "Барселона — Атлетико",
            "type": "foot",
            "desc": "Ла Лига. Важнейший матч за 2-е место."
        }
    ]

def generate_all_data():
    try:
        print("--- Сбор данных начат ---")
        
        navi_events = fetch_navi_matches()
        foot_events = fetch_football_matches()
        
        # Базовые события (игры AAA)
        base_events = [
            {
                "id": "game_1",
                "date": "2026-04-17",
                "title": "Pragmata Release",
                "type": "game",
                "desc": "AAA-экшен от Capcom."
            }
        ]
        
        all_events = navi_events + foot_events + base_events
        
        # Сохранение
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(all_events, f, ensure_ascii=False, indent=4)
            
        print(f"Успешно сохранено {len(all_events)} событий.")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    generate_all_data()
