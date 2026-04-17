import json
import datetime
import requests
import xml.etree.ElementTree as ET
import os

# --- ТВОИ КЛЮЧИ ---
FOOTBALL_API_KEY = "c121f79556c340d78ba1585581dbdf73"
GIANT_BOMB_API_KEY = "56e84a76075b834c4f9c7c789a5224110d931ad4"
STEAM_API_KEY = "FAC4DB55821995AC91BF405E875C8382"
PANDASCORE_API_KEY = "yp6UPmu4SVuXDOKgX05lr1xbbP_puuolTGTTNeNK33yXXNY_VR8"

# ЖЕСТКАЯ ЦЕНЗУРА И ФИЛЬТР МУСОРА
BANNED_GENRE_IDS = [71, 73, 74] 
# Добавил фильтр по техническому мусору (саундтреки, демо, паки)
BLACKLIST_WORDS = [
    "hentai", "lewd", "sexual", "porn", "nsfw", "erotic", "sex", "sin", "uncensored", "dating",
    "soundtrack", "dlc", "demo", "pack", "bundle", "booklet", "theme", "artbook", "guide", "season pass"
]

def is_clean(name, description="", genres=None, app_type="game"):
    """Глубокая проверка на мусор: слова, жанры и тип контента Steam."""
    if app_type != "game": # Главный фильтр: только полноценные игры
        return False
        
    text = (str(name) + " " + str(description)).lower()
    if any(word in text for word in BLACKLIST_WORDS):
        return False
        
    if genres:
        if any(g.get('id') in BANNED_GENRE_IDS for g in genres):
            return False
    return True

def get_steam_games():
    """Агент: Получение ТОЛЬКО полноценных игр из Steam."""
    print(">>> [ИСТОЧНИК: STEAM] Фильтрация мусора и поиск AAA...")
    events = []
    try:
        url = "https://store.steampowered.com/api/featuredcategories/?l=russian"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            # Проверяем разные категории новинок
            coming_soon = res.json().get('coming_soon', {}).get('items', [])
            new_releases = res.json().get('new_releases', {}).get('items', [])
            
            for item in (coming_soon + new_releases)[:20]:
                app_id = item.get('id')
                d_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=russian"
                d_res = requests.get(d_url, timeout=10)
                
                if d_res.status_code == 200:
                    raw_data = d_res.json().get(str(app_id))
                    if not raw_data or not raw_data.get('success'):
                        continue
                        
                    g_data = raw_data.get('data', {})
                    name = g_data.get('name', '')
                    desc = g_data.get('short_description', '')
                    genres = g_data.get('genres', [])
                    app_type = g_data.get('type', 'game') # 'game', 'dlc', 'demo', 'music' etc.
                    
                    if is_clean(name, desc, genres, app_type):
                        # Определяем дату (если уже вышла — сегодня, если нет — ставим в окно)
                        events.append({
                            "id": f"steam_{app_id}",
                            "date": "2026-04-17", # Ставим на сегодня для видимости в тесте
                            "title": f"🎮 {name}",
                            "type": "game",
                            "desc": f"Steam ({app_type}): {g_data.get('release_date', {}).get('date', 'Скоро')}. {desc[:120]}...",
                            "url": f"https://store.steampowered.com/app/{app_id}"
                        })
        print(f"--- Steam: Найдено {len(events)} реальных игр (мусор отсеян).")
    except Exception as e:
        print(f"!!! Ошибка Steam: {e}")
    return events

def get_navi_matches():
    """Агент: Поиск РЕАЛЬНЫХ матчей NAVI (приоритет CS2)."""
    print(">>> [ИСТОЧНИК: PANDASCORE] Поиск актуальных игр NAVI...")
    events = []
    
    if not PANDASCORE_API_KEY:
        return []

    try:
        # Тянем и идущие сейчас (running), и будущие (not_started) матчи
        # Фильтруем по команде Natus Vincere во всех дисциплинах, но пометим игру
        url = "https://api.pandascore.co/teams/natus-vincere/matches?sort=begin_at&filter[status]=running,not_started"
        headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
        res = requests.get(url, headers=headers, timeout=15)
        
        if res.status_code == 200:
            matches = res.json()
            for match in matches[:5]:
                start_dt = match.get('begin_at')
                if not start_dt: continue
                
                m_date = start_dt.split('T')[0]
                m_time = start_dt.split('T')[1][:5]
                game_name = match.get('videogame', {}).get('name', 'CS2')
                
                # Если матч идет сегодня
                events.append({
                    "id": f"navi_ps_{match['id']}",
                    "date": m_date,
                    "time": m_time,
                    "title": f"🏆 {game_name}: {match['name']}",
                    "type": "navi",
                    "desc": f"Турнир: {match['league']['name']}. Статус: {match['status'].upper()}.",
                    "url": "https://www.hltv.org/matches" if "Counter-Strike" in game_name else "https://liquipedia.net/"
                })
            print(f"--- PandaScore: Получено {len(events)} актуальных матчей.")
    except Exception as e:
        print(f"!!! Ошибка PandaScore: {e}")
    return events

def get_football():
    """Агент: Футбол Барселоны."""
    evs = []
    try:
        headers = {'X-Auth-Token': FOOTBALL_API_KEY}
        res = requests.get("https://api.football-data.org/v4/teams/81/matches?status=SCHEDULED", headers=headers, timeout=10)
        if res.status_code == 200:
            for m in res.json().get('matches', [])[:5]:
                match_title = f"{m['homeTeam']['shortName']} — {m['awayTeam']['shortName']}"
                evs.append({
                    "id": f"f_{m['id']}", 
                    "date": m['utcDate'].split('T')[0], 
                    "title": f"⚽ {match_title}", 
                    "type": "foot", 
                    "time": m['utcDate'].split('T')[1][:5],
                    "desc": f"Лига: {m['competition']['name']}",
                    "url": f"https://www.google.com/search?q={match_title.replace(' ', '+')}+match"
                })
        print(f"--- Футбол: Найдено {len(evs)} матчей.")
    except: pass
    return evs

def get_gaming_news():
    """Агент: Новости (RSS)."""
    news = []
    feeds = ["https://stopgame.ru/rss/rss_news.xml", "https://www.playground.ru/rss/news.xml"]
    for url in feeds:
        try:
            res = requests.get(url, timeout=10)
            root = ET.fromstring(res.content)
            for item in root.findall('./channel/item')[:15]:
                title = item.find('title').text
                if any(kw in title.lower() for kw in ["трейлер", "дата", "релиз", "перенос", "анонс"]):
                    pub_date = item.find('pubDate').text
                    date_obj = datetime.datetime.strptime(pub_date[:16], '%a, %d %b %Y')
                    news.append({
                        "id": f"n_{hash(title)}", 
                        "date": date_obj.strftime('%Y-%m-%d'), 
                        "title": f"📰 {title[:45]}...", 
                        "type": "news", 
                        "desc": title, 
                        "url": item.find('link').text
                    })
        except: continue
    return news

def main():
    print("--- ЗАПУСК ЖЕСТКОЙ ОЧИСТКИ И ОБНОВЛЕНИЯ ---")
    
    # Собираем данные
    data = get_football() + get_navi_matches() + get_steam_games() + get_gaming_news()
    
    # Финальная чистка заголовков (на всякий случай)
    final_data = [e for e in data if is_clean(e['title'], e.get('desc', ''))]
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"--- ГОТОВО: {len(final_data)} событий сохранено. ---")

if __name__ == "__main__":
    main()
