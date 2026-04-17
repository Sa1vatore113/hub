import json
import datetime
import requests
import xml.etree.ElementTree as ET
import os

# --- ТВОИ КЛЮЧИ ---
FOOTBALL_API_KEY = "c121f79556c340d78ba1585581dbdf73" 
GIANT_BOMB_API_KEY = "56e84a76075b834c4f9c7c789a5224110d931ad4"

def get_real_games():
    """Агент: Получение AAA-релизов через Giant Bomb API."""
    events = []
    if not GIANT_BOMB_API_KEY:
        print("Giant Bomb: Ключ API отсутствует.")
        return []

    try:
        print("Агент: Запрашиваю список игр на 2026 год у Giant Bomb...")
        url = "https://www.giantbomb.com/api/games/"
        params = {
            'api_key': GIANT_BOMB_API_KEY,
            'format': 'json',
            'filter': 'original_release_date:2026-01-01|2026-12-31',
            'sort': 'original_release_date:asc',
            'limit': 30,
            'field_list': 'name,original_release_date,deck,image'
        }
        # Giant Bomb крайне чувствителен к User-Agent. Используем уникальное имя.
        headers = {
            'User-Agent': 'GamerHubBot_User_Sa1vatore113/2.0 (Educational Project)',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('error') != 'OK':
                print(f"Giant Bomb Error: {data.get('error')}")
                return []
                
            results = data.get('results', [])
            for game in results:
                rel_date = game.get('original_release_date')
                if rel_date:
                    clean_date = rel_date.split(' ')[0]
                    events.append({
                        "id": f"gb_{game['name']}_{clean_date}",
                        "date": clean_date,
                        "title": f"🎮 {game['name']}",
                        "type": "game",
                        "desc": f"{game.get('deck', 'Крупный релиз 2026 года. Подробности появятся позже.')}"
                    })
            print(f"Giant Bomb: Успешно найдено {len(events)} игр.")
        else:
            print(f"Giant Bomb HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"Критическая ошибка Giant Bomb API: {e}")
    
    return events

def get_gaming_news():
    """Агент: Поиск свежих трейлеров и новостей на русском."""
    print("Агент: Проверка RSS-лент на наличие трейлеров...")
    news_events = []
    feeds = [
        "https://stopgame.ru/rss/rss_news.xml",
        "https://www.playground.ru/rss/news.xml"
    ]
    keywords = ["Трейлер", "Перенос", "Дата выхода", "Геймплей", "Анонс", "Релиз", "Delayed", "Тизер"]
    
    for url in feeds:
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if res.status_code == 200:
                # Очистка от возможных проблем с кодировкой
                content = res.content.decode('utf-8', errors='ignore')
                root = ET.fromstring(content)
                for item in root.findall('./channel/item')[:15]:
                    title = item.find('title').text
                    pub_date = item.find('pubDate').text
                    
                    if any(kw.lower() in title.lower() for kw in keywords):
                        try:
                            # Стандартный формат даты RSS: Sat, 17 Apr 2026 12:00:00 +0300
                            date_obj = datetime.datetime.strptime(pub_date[:16], '%a, %d %b %Y')
                            news_events.append({
                                "id": f"news_{hash(title)}",
                                "date": date_obj.strftime('%Y-%m-%d'),
                                "title": f"📰 {title[:50]}...",
                                "type": "news",
                                "desc": title
                            })
                        except Exception as date_e:
                            continue
        except Exception as e:
            print(f"Ошибка при обработке ленты {url}: {e}")
            
    print(f"Новости: Найдено {len(news_events)} актуальных новостей.")
    return news_events

def get_football():
    """Агент: Матчи Барселоны."""
    events = []
    try:
        url = "https://api.football-data.org/v4/teams/81/matches?status=SCHEDULED"
        headers = {'X-Auth-Token': FOOTBALL_API_KEY}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for m in data.get('matches', [])[:5]:
                events.append({
                    "id": f"foot_{m['id']}",
                    "date": m['utcDate'].split('T')[0],
                    "title": f"⚽ {m['homeTeam']['shortName']} — {m['awayTeam']['shortName']}",
                    "type": "foot",
                    "time": m['utcDate'].split('T')[1][:5],
                    "desc": f"{m['competition']['name']}. Camp Nou."
                })
            print(f"Футбол: Найдено {len(events)} матчей.")
        else:
            print(f"Football API Error: {res.status_code}")
    except Exception as e:
        print(f"Ошибка футбольного API: {e}")
    return events

def get_navi():
    """Агент: Ручной контроль матчей NAVI."""
    # Генерируем матч на сегодня для теста системы
    today = datetime.date.today()
    return [{
        "id": "navi_major_2026",
        "date": today.isoformat(),
        "title": "🏆 NAVI — FaZe Clan",
        "type": "navi",
        "time": "19:30",
        "desc": "PGL Major 2026. Решающая битва. Смотрим на официальных каналах."
    }]

def main():
    print(f"--- ЗАПУСК ЦИКЛА ОБНОВЛЕНИЯ: {datetime.datetime.now()} ---")
    
    # Сбор данных с защитой от пустых списков
    try:
        game_data = get_real_games()
        news_data = get_gaming_news()
        foot_data = get_football()
        navi_data = get_navi()
        
        all_events = game_data + news_data + foot_data + navi_data
        
        if not all_events:
            print("ПРЕДУПРЕЖДЕНИЕ: События не найдены. Проверьте ключи и интернет-соединение.")
        
        # Сохранение в файл
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(all_events, f, ensure_ascii=False, indent=4)
            
        print(f"--- УСПЕХ: data.json обновлен ({len(all_events)} событий) ---")
        
    except Exception as e:
        print(f"Критическая ошибка в главном цикле: {e}")
        # Создаем пустой список, чтобы сайт не упал окончательно
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump([], f)

if __name__ == "__main__":
    main()
