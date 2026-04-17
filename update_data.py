import json
import datetime
import requests
import xml.etree.ElementTree as ET
import os

# --- ТВОИ КЛЮЧИ ---
FOOTBALL_API_KEY = "c121f79556c340d78ba1585581dbdf73"
GIANT_BOMB_API_KEY = "56e84a76075b834c4f9c7c789a5224110d931ad4"
STEAM_API_KEY = "FAC4DB55821995AC91BF405E875C8382"

def get_steam_games():
    """Агент: Получение данных о грядущих играх через Steam API со ссылками."""
    print(">>> [ИСТОЧНИК: STEAM API] Проверка данных в Steam...")
    events = []
    if not STEAM_API_KEY:
        return []

    target_apps = [
        {"id": "1271710", "title": "Hytale"},
        {"id": "1931730", "title": "Project LLL"},
        {"id": "2669300", "title": "Pragmata"}
    ]
    
    try:
        for app in target_apps:
            url = f"https://store.steampowered.com/api/appdetails?appids={app['id']}&l=russian"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json().get(app['id'])
                if data and data.get('success'):
                    info = data['data']
                    events.append({
                        "id": f"steam_{app['id']}",
                        "date": "2026-06-15",
                        "title": f"🎮 {info['name']}",
                        "type": "game",
                        "desc": f"Steam: {info.get('short_description', '')[:120]}...",
                        "url": f"https://store.steampowered.com/app/{app['id']}" # Ссылка на Steam
                    })
        print(f"--- Успех: Steam вернул данные по {len(events)} играм.")
    except Exception as e:
        print(f"!!! Ошибка Steam: {e}")
    return events

def get_real_games():
    """Агент: Поиск реальных релизов 2026 года через Giant Bomb со ссылками."""
    print(">>> [ИСТОЧНИК: GIANT BOMB] Ищу игры на 2026 год...")
    events = []
    seen_titles = set()
    if GIANT_BOMB_API_KEY:
        try:
            url = "https://www.giantbomb.com/api/games/"
            params = {
                'api_key': GIANT_BOMB_API_KEY,
                'format': 'json',
                'filter': 'expected_release_year:2026',
                'sort': 'original_release_date:asc',
                'limit': 40,
                'field_list': 'name,original_release_date,deck,site_detail_url' # Добавили ссылку
            }
            headers = {'User-Agent': 'GamerHubBot/3.0'}
            res = requests.get(url, params=params, headers=headers, timeout=15)
            if res.status_code == 200:
                results = res.json().get('results', [])
                for game in results:
                    name = game['name']
                    date_str = game.get('original_release_date', "2026-06-15").split(' ')[0]
                    events.append({
                        "id": f"gb_{hash(name)}",
                        "date": date_str,
                        "title": f"🎮 {name}",
                        "type": "game",
                        "desc": game.get('deck', 'Релиз из Giant Bomb.'),
                        "url": game.get('site_detail_url') # Ссылка на Giant Bomb
                    })
                    seen_titles.add(name.lower())
                print(f"--- Успех: Найдено {len(results)} игр.")
        except Exception as e:
            print(f"!!! Ошибка Giant Bomb: {e}")
    
    # Резерв
    golden = [{"date": "2026-10-24", "title": "Grand Theft Auto VI", "desc": "Главный релиз.", "url": "https://www.rockstargames.com/VI"}]
    for item in golden:
        if item['title'].lower() not in seen_titles:
            events.append({
                "id": f"gold_{hash(item['title'])}", 
                "date": item['date'], 
                "title": f"🎮 {item['title']} [HIT]", 
                "type": "game", 
                "desc": item['desc'],
                "url": item['url']
            })
    return events

def get_gaming_news():
    """Агент: Новости со ссылками на статьи."""
    print(">>> [ИСТОЧНИК: RSS] Сканирую ленты...")
    news = []
    feeds = ["https://stopgame.ru/rss/rss_news.xml", "https://www.playground.ru/rss/news.xml"]
    for url in feeds:
        try:
            res = requests.get(url, timeout=10)
            root = ET.fromstring(res.content)
            for item in root.findall('./channel/item')[:10]:
                title = item.find('title').text
                link = item.find('link').text # Извлекаем ссылку
                if any(kw in title.lower() for kw in ["трейлер", "дата", "релиз", "перенос"]):
                    pub_date = item.find('pubDate').text
                    date_obj = datetime.datetime.strptime(pub_date[:16], '%a, %d %b %Y')
                    news.append({
                        "id": f"n_{hash(title)}", 
                        "date": date_obj.strftime('%Y-%m-%d'), 
                        "title": f"📰 {title[:40]}...", 
                        "type": "news", 
                        "desc": title,
                        "url": link # Ссылка на новость
                    })
        except: continue
    print(f"--- Найдено {len(news)} новостей.")
    return news

def get_football():
    """Агент: Футбол со ссылкой на поиск матча."""
    print(">>> [ИСТОЧНИК: FOOTBALL] Запрашиваю матчи...")
    evs = []
    try:
        headers = {'X-Auth-Token': FOOTBALL_API_KEY}
        res = requests.get("https://api.football-data.org/v4/teams/81/matches?status=SCHEDULED", headers=headers, timeout=10)
        for m in res.json().get('matches', [])[:5]:
            match_title = f"{m['homeTeam']['shortName']} — {m['awayTeam']['shortName']}"
            evs.append({
                "id": f"f_{m['id']}", 
                "date": m['utcDate'].split('T')[0], 
                "title": f"⚽ {match_title}", 
                "type": "foot", 
                "desc": m['competition']['name'],
                "url": f"https://www.google.com/search?q={match_title.replace(' ', '+')}+match" # Ссылка на Google Search матча
            })
        print(f"--- Успех: {len(evs)} матчей.")
    except Exception as e:
        print(f"!!! Ошибка футбола: {e}")
    return evs

def main():
    print("--- ЗАПУСК ОБНОВЛЕНИЯ ---")
    data = get_football() + get_real_games() + get_gaming_news() + get_steam_games()
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"--- ГОТОВО: {len(data)} событий со ссылками. ---")

if __name__ == "__main__":
    main()
