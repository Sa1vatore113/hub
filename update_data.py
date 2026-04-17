import json
import datetime
import requests
import xml.etree.ElementTree as ET
import os

# Твой рабочий ключ для футбола
FOOTBALL_API_KEY = "c121f79556c340d78ba1585581dbdf73"

def get_gaming_news():
    """Агент: Получение свежих новостей через русскоязычные RSS ленты."""
    print("Агент: Ищу свежие трейлеры и анонсы на русском...")
    news_events = []
    
    # Русскоязычные игровые ленты
    feeds = [
        "https://stopgame.ru/rss/rss_news.xml",
        "https://www.playground.ru/rss/news.xml"
    ]
    
    # Ключевые слова на русском
    keywords = ["Трейлер", "Перенос", "Дата выхода", "Геймплей", "Анонс", "Релиз", "Выйдет"]
    
    for url in feeds:
        try:
            # Добавляем User-Agent, чтобы сайты не блокировали робота
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                # Парсинг RSS (структура может чуть отличаться у разных сайтов)
                items = root.findall('./channel/item')
                for item in items[:20]:
                    title = item.find('title').text
                    link = item.find('link').text
                    pub_date = item.find('pubDate').text
                    
                    # Фильтруем по ключевым словам
                    if any(word.lower() in title.lower() for word in keywords):
                        # Парсим дату (обычно формат: Tue, 17 Apr 2026...)
                        try:
                            date_obj = datetime.datetime.strptime(pub_date[:16], '%a, %d %b %Y')
                        except:
                            date_obj = datetime.datetime.now() # Если формат даты сбоит

                        news_events.append({
                            "id": f"news_{hash(title)}",
                            "date": date_obj.strftime('%Y-%m-%d'),
                            "title": f"📰 {title[:45]}...",
                            "type": "news",
                            "time": date_obj.strftime('%H:%M'),
                            "desc": f"{title}. Источник: {url.split('/')[2]}"
                        })
        except Exception as e:
            print(f"Ошибка при чтении ленты {url}: {e}")
            
    return news_events

def get_football():
    """Матчи Барселоны на русском."""
    events = []
    if not FOOTBALL_API_KEY: return events
    try:
        url = "https://api.football-data.org/v4/teams/81/matches?status=SCHEDULED"
        headers = {'X-Auth-Token': FOOTBALL_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            for m in response.json().get('matches', [])[:5]:
                # Переводим названия турниров на лету для красоты
                comp = m['competition']['name']
                if "Primera Division" in comp: comp = "Ла Лига"
                if "UEFA Champions League" in comp: comp = "Лига Чемпионов"
                
                events.append({
                    "id": f"foot_{m['id']}",
                    "date": m['utcDate'].split('T')[0],
                    "title": f"⚽ {m['homeTeam']['shortName']} — {m['awayTeam']['shortName']}",
                    "type": "foot",
                    "time": m['utcDate'].split('T')[1][:5],
                    "desc": f"Турнир: {comp}. Стадион: {m.get('venue', 'Неизвестно')}"
                })
    except: pass
    return events

def get_navi():
    """События NAVI на русском."""
    today = datetime.date.today()
    return [{
        "id": "navi_1",
        "date": today.isoformat(),
        "title": "🏆 NAVI — FaZe Clan",
        "type": "navi",
        "time": "19:30",
        "desc": "Матч в рамках PGL Major 2026. Прямая трансляция на YouTube/Twitch."
    }]

def main():
    print("--- ЗАПУСК РУССКОЯЗЫЧНОГО АГЕНТА (НОВОСТИ + ИГРЫ + СПОРТ) ---")
    
    # Собираем все данные вместе
    all_events = get_gaming_news() + get_football() + get_navi()
    
    # Сохраняем в JSON для нашего сайта
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(all_events, f, ensure_ascii=False, indent=4)
        print(f"УСПЕХ: Календарь обновлен. Найдено {len(all_events)} событий на русском.")
    except Exception as e:
        print(f"Ошибка записи файла: {e}")

if __name__ == "__main__":
    main()
