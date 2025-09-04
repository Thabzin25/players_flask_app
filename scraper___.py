import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd

# ---------------- CONFIG ----------------
LEAGUES = {
    "Premier League": 9,
    "La Liga": 12,
    "Serie A": 11,
    "Bundesliga": 20,
    "Ligue 1": 13
}
SEASONS = ["2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

# ---------------- FUNCTIONS ----------------
def scrape_season(league_name, league_id, season):
    url = f"https://fbref.com/en/comps/{league_id}/{league_name.replace(' ', '-')}-Stats/{season}/players/"
    print(f"[INFO] Scraping {league_name} {season}...")
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print(f"  ❌ Error fetching URL: {e}")
        return None
    
    soup = BeautifulSoup(res.text, "html.parser")
    tables = []

    # Normal table
    normal_table = soup.find("table", {"id": "stats_standard"})
    if normal_table:
        tables.append(pd.read_html(str(normal_table))[0])

    # Tables hidden in comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for c in comments:
        if "stats_standard" in c:
            try:
                df = pd.read_html(c)[0]
                tables.append(df)
            except:
                continue

    if not tables:
        print(f"  ⚠️ No tables found for {league_name} {season}")
        return None

    df_combined = pd.concat(tables, ignore_index=True)
    df_combined["League"] = league_name
    df_combined["Season"] = season
    return df_combined

# ---------------- MAIN ----------------
all_data = []
for league_name, league_id in LEAGUES.items():
    for season in SEASONS:
        df_season = scrape_season(league_name, league_id, season)
        if df_season is not None:
            all_data.append(df_season)

if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv("fbref_player_stats.csv", index=False)
    print(f"[DONE] Saved {len(final_df)} player rows to fbref_player_stats.csv")
else:
    print("[DONE] No data scraped.")
