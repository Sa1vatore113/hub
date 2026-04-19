import json
import datetime
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re

# --- ТВОИ КЛЮЧИ ---
FOOTBALL_API_KEY = "c121f79556c340d78ba1585581dbdf73"
PANDASCORE_API_KEY = "yp6UPmu4SVuXDOKgX05lr1xbbP_puuolTGTTNeNK33yXXNY_VR8"

def get_stopgame_dates():
    """Агент: Парсинг календаря релизов с StopGame.ru (PC игры)."""
    print(">>> [ИСТОЧНИК: STOPGAME CALENDAR] Читаю даты релизов...")
    events = []
    url = "https://stopgame.ru/games/dates/pc"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"--- Ошибка доступа к StopGame: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'lxml')
        # На StopGame игры обычно лежат в блоках по датам
        # Ищем карточки игр
        items = soup.find_all('div', class_=re.compile(r'item|_card_'))
        
        for item in items[:30]:
            try:
                # Находим название
                title_tag = item.find(['a', 'div'], class_=re.compile(r'title|name'))
                if not title_tag: continue
                name = title_tag.text.strip()

                # Находим дату
                date_tag = item.find('div', class_=re.compile(r'date|release'))
                if not date_tag: continue
                date_text = date_tag.text.strip() # Например: "17 апреля 2026"

                # Ссылка на игру
                link_tag = item.find('a', href=True)
                game_url = "https://stopgame.ru" + link_tag['href'] if link_tag else url

                # Конвертируем "17 апреля 2026" в "2026-04-17"
                months = {
                    'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
                    'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
                    'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
                }
                
                parts = date_text.lower().split()
                if len(parts) >= 3:
                    day = parts[0].zfill(2)
                    month = months.get(parts[1], '01')
                    year = parts[2]
                    clean_date = f"{year}-{month}-{day}"

                    events.append({
                        "id": f"sg_{hash(name)}",
                        "date": clean_date,
                        "title": f"🎮 {name}",
                        "type": "game",
                        "desc": f"Ожидаемый релиз на PC по данным StopGame. Дата: {date_text}",
                        "url": game_url
                    })
            except Exception as e:
                continue

        print(f"--- StopGame: Успешно найдено {len(events)} игр.")
    except Exception as e:
        print(f"!!! Ошибка парсинга StopGame: {e}")
    
    return events

def get_navi_matches():
    """Агент: Поиск РЕАЛЬНЫХ матчей NAVI по Counter-Strike 2."""
    print(">>> [ИСТОЧНИК: PANDASCORE] Поиск матчей NAVI (CS2)...")
    events = []
    if not PANDASCORE_API_KEY: return []

    try:
        url = "https://api.pandascore.co/csgo/matches?filter[status]=running,not_started&sort=begin_at"
        headers = {"Authorization": f"Bearer {PANDASCORE_API_KEY}"}
        res = requests.get(url, headers=headers, timeout=15)
        
        if res.status_code == 200:
            matches = res.json()
            for m in matches:
                opponents = [op['opponent']['name'].lower() for op in m.get('opponents', [])]
                if any(x in opponents for x in ['natus vincere', 'navi']):
                    start_dt = m.get('begin_at')
                    if not start_dt: continue
                    
                    dt = datetime.datetime.strptime(start_dt, "%Y-%m-%dT%H:%M:%SZ")
                    dt_local = dt + datetime.timedelta(hours=3) # Коррекция времени
                    
                    events.append({
                        "id": f"navi_cs_{m['id']}",
                        "date": dt_local.strftime('%Y-%m-%d'),
                        "time": dt_local.strftime('%H:%M'),
                        "title": f"🏆 CS2: {m['name']}",
                        "type": "navi",
                        "desc": f"Турнир: {m['league']['name']}. Статус: {m['status'].upper()}.",
                        "url": "https://www.hltv.org/matches"
                    })
            print(f"--- PandaScore: Получено {len(events)} матчей NAVI.")
    except Exception as e:
        print(f"!!! Ошибка PandaScore: {e}")
    return events

def get_football():
    """Агент: Барселона."""
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
    print("--- ЗАПУСК ОБНОВЛЕНИЯ (ИСТОЧНИК: STOPGAME) ---")
    # Собираем данные
    data = get_football() + get_navi_matches() + get_stopgame_dates() + get_gaming_news()
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"--- ГОТОВО: {len(data)} событий сохранено. ---")

if __name__ == "__main__":
    main()
