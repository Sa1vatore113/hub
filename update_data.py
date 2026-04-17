import json
import datetime
import requests
import xml.etree.ElementTree as ET
import os

# --- ТВОИ КЛЮЧИ (ПОЛНЫЙ НАБОР) ---
FOOTBALL_API_KEY = "c121f79556c340d78ba1585581dbdf73"
GIANT_BOMB_API_KEY = "56e84a76075b834c4f9c7c789a5224110d931ad4"
STEAM_API_KEY = "FAC4DB55821995AC91BF405E875C8382"

def get_steam_games():
    """Агент: Получение данных о грядущих играх через Steam API."""
    events = []
    # Если ключа нет, не падаем, а просто пропускаем
    if not STEAM_API_KEY:
        print(">>> [ИСТОЧНИК: STEAM API] Ключ отсутствует. Пропуск.")
        return []

    print(">>> [ИСТОЧНИК: STEAM API] Проверка данных в Steam...")
    # Список AppID для мониторинга (игры, у которых уже есть страницы)
    target_apps = [
        {"id": "1271710", "title": "Hytale"},
        {"id": "1931730", "title": "Project LLL"},
        {"id": "2669300", "title": "Pragmata"}
    ]
    
    try:
        for app in target_apps:
            # Steam Store API работает и без ключа, но Web API Key нужен для других функций
            url = f"https://store.steampowered.com/api/appdetails?appids={app['id']}&l=russian"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json().get(app['id'])
                if data and data.get('success'):
                    info = data['data']
                    events.append({
                        "id": f"steam_{app['id']}",
                        "date": "2026-06-15", # Ожидаемая дата для невышедших
                        "title": f"🎮 {info['name']}",
                        "type": "game",
                        "desc": f"Steam: {info.get('short_description', 'Описание скоро появится.')[:150]}..."
                    })
        print(f"--- Успех: Steam вернул данные по {len(events)} играм.")
    except Exception as e:
        print(f"!!! Ошибка Steam API: {e}")
    return events

def get_real_games():
    """Агент: Поиск реальных релизов 2026 года через Giant Bomb."""
    events = []
    seen_titles = set()

    if GIANT_BOMB_API_KEY:
        try:
            print(">>> [ИСТОЧНИК: GIANT BOMB] Ищу игры на 2026 год...")
            url = "https://www.giantbomb.com/api/games/"
            params = {
                'api_key': GIANT_BOMB_API_KEY,
                'format': 'json',
                'filter': 'expected_release_year:2026',
                'sort': 'original_release_date:asc',
                'limit': 40,
                'field_list': 'name,original_release_date,deck,expected_release_month'
            }
            headers = {'User-Agent': 'GamerHubBot/3.0 (Sa1vatore113)'}
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                print(f"--- Успех: База вернула {len(results)} игр.")
                for game in results:
                    name = game['name']
                    date_str = game.get('original_release_date', "2026-06-15").split(' ')[0]
                    events.append({
                        "id": f"gb_{hash(name)}",
                        "date": date_str,
                        "title": f"🎮 {name}",
                        "type": "game",
                        "desc": game.get('deck', 'Реальный релиз из базы Giant Bomb.')
                    })
                    seen_titles.add(name.lower())
        except Exception as e:
            print(f"!!! Ошибка Giant Bomb: {e}")

    # Золотой список (Заглушки)
    golden = [
        {"date": "2026-10-24", "title": "Grand Theft Auto VI", "desc": "Главный мировой релиз. Возвращение в Вайс-Сити."},
        {"date": "2026-04-17", "title": "Pragmata", "desc": "Загадочный экшен от Capcom."}
    ]
    
    added_golden = 0
    for item in golden:
        if item['title'].lower() not in seen_titles:
            events.append({
                "id": f"gold_{hash(item['title'])}",
                "date": item['date'],
                "title": f"🎮 {item['title']} [HIT]",
                "type": "game",
                "desc": item['desc']
            })
            added_golden += 1
    print(f">>> [РЕЗЕРВ] Добавлено {added_golden} игр из золотого списка.")
            
    return events

def get_gaming_news():
    """Агент: Поиск живых новостей."""
    print(">>> [ИСТОЧНИК: RSS НОВОСТИ] Сканирую ленты...")
    news_events = []
    feeds = ["https://stopgame.ru/rss/rss_news.xml", "https://www.playground.ru/rss/news.xml"]
    
    for url in feeds:
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                found = 0
                for item in root.findall('./channel/item')[:10]:
                    title = item.find('title').text
                    pub_date = item.find('pubDate').text
                    # Берем только важные новости
                    if any(kw in title.lower() for kw in ["трейлер", "дата", "релиз", "перенос", "геймплей"]):
                        date_obj = datetime.datetime.strptime(pub_date[:16], '%a, %d %b %Y')
                        news_events.append({
                            "id": f"news_{hash(title)}",
                            "date": date_obj.strftime('%Y-%m-%d'),
                            "title": f"📰 {title[:45]}...",
                            "type": "news",
                            "desc": f"Свежая новость от {url.split('.')[0].split('//')[1]}: {title}"
                        })
                        found += 1
                print(f"--- Найдено {found} живых новостей в {url.split('/')[2]}")
        except: continue
    return news_events

def get_football():
    """Агент: Матчи Барселоны."""
    print(">>> [ИСТОЧНИК: FOOTBALL API] Запрашиваю матчи...")
    events = []
    try:
        url = "https://api.football-data.org/v4/teams/81/matches?status=SCHEDULED"
        headers = {'X-Auth-Token': FOOTBALL_API_KEY}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            matches = res.json().get('matches', [])
            for m in matches[:5]:
                events.append({
                    "id": f"foot_{m['id']}",
                    "date": m['utcDate'].split('T')[0],
                    "title": f"⚽ {m['homeTeam']['shortName']} — {m['awayTeam']['shortName']}",
                    "type": "foot",
                    "time": m['utcDate'].split('T')[1][:5],
                    "desc": f"Реальный матч: {m['competition']['name']}. Удачи Барсе!"
                })
            print(f"--- Успех: Найдено {len(events)} реальных матчей.")
        else:
            print(f"!!! Ошибка API футбола: {res.status_code}")
    except: pass
    return events

def main():
    print(f"\n--- СТАРТ ПРОВЕРКИ СИСТЕМ ---")
    
    # Собираем данные из всех источников
    all_data = get_football() + get_real_games() + get_gaming_news() + get_steam_games()
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n--- ИТОГ: data.json обновлен. Всего событий: {len(all_data)} ---")

if __name__ == "__main__":
    main()
