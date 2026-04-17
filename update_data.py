import json
import datetime
import requests
import xml.etree.ElementTree as ET
import os

# --- ТВОИ КЛЮЧИ (ПОЛНЫЙ КОМПЛЕКТ) ---
FOOTBALL_API_KEY = "c121f79556c340d78ba1585581dbdf73"
GIANT_BOMB_API_KEY = "56e84a76075b834c4f9c7c789a5224110d931ad4"
STEAM_API_KEY = "FAC4DB55821995AC91BF405E875C8382"
PANDASCORE_API_KEY = "yp6UPmu4SVuXDOKgX05lr1xbbP_puuolTGTTNeNK33yXXNY_VR8"

# ЖЕСТКАЯ ЦЕНЗУРА (ID жанров Steam: 71 - Nudity, 73 - Hentai)
BANNED_GENRE_IDS = [71, 73, 74] 
BLACKLIST_WORDS = ["hentai", "lewd", "sexual", "porn", "nsfw", "erotic", "sex", "sin", "uncensored", "dating"]

def is_clean(name, description="", genres=None):
    """Проверка игры на чистоту: по словам и по ID жанров Steam."""
    text = (str(name) + " " + str(description)).lower()
    if any(word in text for word in BLACKLIST_WORDS):
        return False
    if genres:
        if any(g.get('id') in BANNED_GENRE_IDS for g in genres):
            return False
    return True

def get_steam_games():
    """Агент: Получение РЕАЛЬНЫХ новинок из Steam с глубокой фильтрацией."""
    print(">>> [ИСТОЧНИК: STEAM] Ищу чистые новинки...")
    events = []
    try:
        url = "https://store.steampowered.com/api/featuredcategories/?l=russian"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            coming_soon = res.json().get('coming_soon', {}).get('items', [])
            for item in coming_soon[:15]:
                app_id = item.get('id')
                d_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=russian"
                d_res = requests.get(d_url, timeout=10)
                if d_res.status_code == 200:
                    g_data = d_res.json().get(str(app_id), {}).get('data', {})
                    if g_data:
                        name = g_data.get('name', '')
                        desc = g_data.get('short_description', '')
                        genres = g_data.get('genres', [])
                        
                        if is_clean(name, desc, genres):
                            # Для Steam новинок ставим дату в текущем месяце для наглядности
                            events.append({
                                "id": f"steam_{app_id}",
                                "date": "2026-04-20", 
                                "title": f"🎮 {name}",
                                "type": "game",
                                "desc": f"Steam Release: {g_data.get('release_date', {}).get('date', 'Скоро')}. {desc[:100]}...",
                                "url": f"https://store.steampowered.com/app/{app_id}"
                            })
        print(f"--- Steam: Найдено {len(events)} проверенных игр.")
    except Exception as e:
        print(f"!!! Ошибка Steam: {e}")
    return events

def get_navi_matches():
    """Агент: Получение РЕАЛЬНЫХ матчей NAVI через PandaScore API."""
    print(">>> [ИСТОЧНИК: PANDASCORE] Ищу реальные игры NAVI...")
    events = []
    
    if not PANDASCORE_API_KEY:
        return []

    try:
        # Запрашиваем будущие матчи команды Natus Vincere
        url = "https://api.pandascore.co/teams/natus-vincere/matches?sort=begin_at&filter[future]=true"
        headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
        res = requests.get(url, headers=headers, timeout=15)
        
        if res.status_code == 200:
            matches = res.json()
            for match in matches[:5]:
                # Парсим дату и время (begin_at: "2026-04-18T15:00:00Z")
                start_dt = match.get('begin_at')
                if start_dt:
                    m_date = start_dt.split('T')[0]
                    m_time = start_dt.split('T')[1][:5]
                    
                    events.append({
                        "id": f"navi_ps_{match['id']}",
                        "date": m_date,
                        "time": m_time,
                        "title": f"🏆 {match['name']}",
                        "type": "navi",
                        "desc": f"Турнир: {match['league']['name']}. Статус: {match['status'].upper()}. Формат: {match['match_type']}.",
                        "url": "https://www.hltv.org/matches"
                    })
            print(f"--- PandaScore: Успешно получено {len(events)} матчей.")
        else:
            print(f"--- PandaScore Error: {res.status_code}")
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
    print("--- ЗАПУСК ОБНОВЛЕНИЯ (PANDASCORE + STEAM FILTER) ---")
    
    data = get_football() + get_navi_matches() + get_steam_games() + get_gaming_news()
    
    # Финальная чистка от нежелательного контента
    final_data = [e for e in data if is_clean(e['title'], e.get('desc', ''))]
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"--- ГОТОВО: {len(final_data)} событий сохранено. ---")

if __name__ == "__main__":
    main()
