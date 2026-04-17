import json
import datetime
import requests
import xml.etree.ElementTree as ET
import os

# --- ТВОИ КЛЮЧИ (АКТИВИРОВАНЫ) ---
FOOTBALL_API_KEY = "c121f79556c340d78ba1585581dbdf73" 
GIANT_BOMB_API_KEY = "56e84a76075b834c4f9c7c789a5224110d931ad4"

def get_real_games():
    """Агент: Получение AAA-релизов через Giant Bomb API."""
    events = []
    if not GIANT_BOMB_API_KEY:
        return []

    try:
        print("Агент: Запрашиваю список игр на 2026 год у Giant Bomb...")
        url = "https://www.giantbomb.com/api/games/"
        params = {
            'api_key': GIANT_BOMB_API_KEY,
            'format': 'json',
            'filter': 'original_release_date:2026-01-01|2026-12-31',
            'sort': 'original_release_date:asc',
            'limit': 20,
            'field_list': 'name,original_release_date,deck'
        }
        # Giant Bomb требует User-Agent
        headers = {'User-Agent': 'GamerHubCalendarBot/1.0 (Personal Project)'}
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            for game in results:
                rel_date = game.get('original_release_date')
                if rel_date:
                    clean_date = rel_date.split(' ')[0]
                    events.append({
                        "id": f"gb_{game['name']}",
                        "date": clean_date,
                        "title": f"🎮 {game['name']}",
                        "type": "game",
                        "desc": f"{game.get('deck', 'Крупный релиз 2026 года. Подробности уточняются.')}"
                    })
            print(f"Giant Bomb: Успешно найдено {len(events)} игр.")
    except Exception as e:
        print(f"Ошибка Giant Bomb API: {e}")
    
    return events

def get_gaming_news():
    """Агент: Поиск свежих трейлеров и новостей на русском."""
    print("Агент: Проверяю StopGame и Playground на наличие трейлеров...")
    news_events = []
    feeds = [
        "https://stopgame.ru/rss/rss_news.xml",
        "https://www.playground.ru/rss/news.xml"
    ]
    # Ключевые слова для фильтрации важных событий
    keywords = ["Трейлер", "Перенос", "Дата выхода", "Геймплей", "Анонс", "Релиз", "Delayed"]
    
    for url in feeds:
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall('./channel/item')[:15]:
                    title = item.find('title').text
                    pub_date = item.find('pubDate').text
                    
                    if any(kw.lower() in title.lower() for kw in keywords):
                        # Парсим дату новости
                        try:
                            date_obj = datetime.datetime.strptime(pub_date[:16], '%a, %d %b %Y')
                            news_events.append({
                                "id": f"news_{hash(title)}",
                                "date": date_obj.strftime('%Y-%m-%d'),
                                "title": f"📰 {title[:45]}...",
                                "type": "news",
                                "desc": title
                            })
                        except: continue
        except: continue
    print(f"Новости: Найдено {len(news_events)} актуальных новостей.")
    return news_events

def get_football():
    """Агент: Матчи Барселоны через Football-Data API."""
    events = []
    try:
        url = "https://api.football-data.org/v4/teams/81/matches?status=SCHEDULED"
        headers = {'X-Auth-Token': FOOTBALL_API_KEY}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            for m in res.json().get('matches', [])[:5]:
                events.append({
                    "id": f"foot_{m['id']}",
                    "date": m['utcDate'].split('T')[0],
                    "title": f"⚽ {m['homeTeam']['shortName']} — {m['awayTeam']['shortName']}",
                    "type": "foot",
                    "time": m['utcDate'].split('T')[1][:5],
                    "desc": f"{m['competition']['name']}. Официальный матч Барселоны."
                })
        print(f"Футбол: Найдено {len(events)} матчей.")
    except: pass
    return events

def get_navi():
    """Агент: Ручной контроль матчей NAVI."""
    today = datetime.date.today()
    # Пока HLTV требует сложного парсинга, держим один "тестовый" матч на сегодня
    return [{
        "id": "navi_current",
        "date": today.isoformat(),
        "title": "🏆 NAVI — FaZe Clan",
        "type": "navi",
        "time": "19:30",
        "desc": "PGL Major 2026. Решающая битва. Не пропусти трансляцию!"
    }]

def main():
    print("--- ЗАПУСК ПОЛНОГО ЦИКЛА ОБНОВЛЕНИЯ ---")
    
    # Собираем данные из всех источников
    game_data = get_real_games()
    news_data = get_gaming_news()
    foot_data = get_football()
    navi_data = get_navi()
    
    all_events = game_data + news_data + foot_data + navi_data
    
    # Сохраняем в файл data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_events, f, ensure_ascii=False, indent=4)
        
    print(f"--- ОБНОВЛЕНИЕ ЗАВЕРШЕНО: Найдено {len(all_events)} событий ---")

if __name__ == "__main__":
    main()
