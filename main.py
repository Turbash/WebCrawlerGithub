"""
GitHub Trending Developers Web Crawler
Scrapes trending developers from GitHub and saves to CSV and JSON
Supports multiple languages and time periods
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
import os
import time
from rich.console import Console
from rich.progress import track, Progress, TaskID
from rich.panel import Panel
from rich.table import Table

GITHUB_BASE_URL = "https://github.com/trending/developers"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
OUTPUT_DIR = "data"
CSV_DIR = os.path.join(OUTPUT_DIR, "csv")
JSON_DIR = os.path.join(OUTPUT_DIR, "json")

LANGUAGES = ["python", "javascript", "typescript", "java", "rust", "go", "c++"]

TIME_PERIODS = ["daily", "weekly", "monthly"]

def setup_directories():
    """Create necessary directories for storing CSV and JSON files"""
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def build_url(language=None, since="daily"):
    """Build GitHub trending developers URL with language and time period"""
    if language:
        return f"{GITHUB_BASE_URL}/{language}?since={since}"
    return f"{GITHUB_BASE_URL}?since={since}"

def scrape_trending_developers(language=None, since="daily"):
    """Scrape trending developers for a specific language and time period"""
    url = build_url(language, since)
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        developers = []
        
        developer_elements = soup.find_all('article', class_='Box-row')
        
        for i, element in enumerate(developer_elements):
            try:
                developer = {
                    'rank': i + 1,
                    'language': language or 'all',
                    'time_period': since
                }
                
                name_link = element.find('h1', class_='h3')
                if name_link:
                    link = name_link.find('a')
                    if link:
                        developer['name'] = link.get_text().strip()
                        developer['profile_url'] = f"https://github.com{link.get('href')}"
                    else:
                        developer['name'] = name_link.get_text().strip()
                        developer['profile_url'] = ""
                else:
                    developer['name'] = ""
                    developer['profile_url'] = ""
                
                username_element = element.find('p', class_='f4')
                if username_element:
                    username_link = username_element.find('a')
                    developer['username'] = username_link.get_text().strip() if username_link else ""
                else:
                    developer['username'] = ""
                
                avatar_img = element.find('img', class_='avatar-user')
                developer['avatar_url'] = avatar_img.get('src', '') if avatar_img else ""
                
                repo_article = element.find('article')
                if repo_article:
                    repo_name_elem = repo_article.find('h1', class_='h4')
                    if repo_name_elem:
                        repo_link = repo_name_elem.find('a')
                        if repo_link:
                            developer['popular_repo'] = repo_link.get_text().strip()
                        else:
                            developer['popular_repo'] = repo_name_elem.get_text().strip()
                    else:
                        developer['popular_repo'] = ""
                    
                    repo_desc_elem = repo_article.find('div', class_='f6 color-fg-muted mt-1')
                    developer['repo_description'] = repo_desc_elem.get_text().strip() if repo_desc_elem else ""
                else:
                    developer['popular_repo'] = ""
                    developer['repo_description'] = ""
                
                if developer['name'] or developer['username']:
                    developer['scraped_at'] = datetime.now().isoformat()
                    developers.append(developer)
                    
            except Exception as e:
                continue
        
        return developers
        
    except requests.RequestException as e:
        return []
    except Exception as e:
        return []

def save_to_csv(developers, filename):
    if not developers:
        return False
    
    fieldnames = ['rank', 'username', 'name', 'repo_description', 'avatar_url', 'profile_url', 'popular_repo', 'language', 'time_period', 'scraped_at']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(developers)
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def save_to_json(developers, filename, language=None, since="daily"):
    if not developers:
        return False
    
    data = {
        'scraped_at': datetime.now().isoformat(),
        'language': language or 'all',
        'time_period': since,
        'total_developers': len(developers),
        'developers': developers
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def display_results(developers):
    console = Console()
    
    if not developers:
        console.print("❌ No developers found", style="red")
        return
    
    table = Table(title="🏆 GitHub Trending Developers", show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Username", style="cyan", width=20)
    table.add_column("Name", style="green", width=25)
    table.add_column("Language", style="yellow", width=12)
    table.add_column("Period", style="blue", width=10)
    table.add_column("Popular Repo", style="yellow", width=25)
    
    for dev in developers[:10]:
        table.add_row(
            str(dev['rank']),
            dev['username'][:18] + "..." if len(dev['username']) > 18 else dev['username'],
            dev['name'][:23] + "..." if len(dev['name']) > 23 else dev['name'],
            dev.get('language', 'all')[:10],
            dev.get('time_period', 'daily')[:8],
            dev['popular_repo'][:23] + "..." if len(dev['popular_repo']) > 23 else dev['popular_repo']
        )
    
    console.print(table)
    
    if len(developers) > 10:
        console.print(f"\n... and {len(developers) - 10} more developers", style="dim")

def scrape_all_combinations():
    """Scrape all language and time period combinations"""
    console = Console()
    console.print(Panel("🚀 GitHub Trending Developers Multi-Language Scraper", style="bold blue"))
    
    all_results = []
    total_combinations = len(LANGUAGES) * len(TIME_PERIODS)
    completed = 0
    
    for language in LANGUAGES:
        for since in TIME_PERIODS:
            completed += 1
            console.print(f"\n[{completed}/{total_combinations}] Scraping {language} - {since}...")
            
            developers = scrape_trending_developers(language, since)
            
            if developers:
                timestamp = get_timestamp()
                
                csv_filename = os.path.join(CSV_DIR, f"github_trending_{language}_{since}_{timestamp}.csv")
                json_filename = os.path.join(JSON_DIR, f"github_trending_{language}_{since}_{timestamp}.json")
                
                csv_saved = save_to_csv(developers, csv_filename)
                json_saved = save_to_json(developers, json_filename, language, since)
                
                if csv_saved and json_saved:
                    console.print(f"✅ Saved {len(developers)} developers for {language} - {since}")
                    all_results.extend(developers)
                else:
                    console.print(f"⚠️  Failed to save some files for {language} - {since}", style="yellow")
            else:
                console.print(f"❌ No data found for {language} - {since}", style="red")
            
            time.sleep(1)
    
    return all_results

def main():
    console = Console()
    
    try:
        setup_directories()
        all_developers = scrape_all_combinations()
        
        if not all_developers:
            console.print("❌ No data scraped from any combination", style="red")
            return
        
        console.print("\n" + "="*80)
        display_results(all_developers)
        
        console.print(f"\n✅ Successfully scraped {len(all_developers)} total developers across all combinations!", style="bold green")
        console.print(f"📁 CSV files saved in: {CSV_DIR}", style="green")
        console.print(f"📁 JSON files saved in: {JSON_DIR}", style="green")
        
        console.print("\n📊 Summary by combination:", style="bold")
        summary_table = Table(show_header=True, header_style="bold cyan")
        summary_table.add_column("Language")
        summary_table.add_column("Period")
        summary_table.add_column("Developers")
        
        summary = {}
        for dev in all_developers:
            key = (dev.get('language', 'all'), dev.get('time_period', 'daily'))
            summary[key] = summary.get(key, 0) + 1
        
        for (lang, period), count in sorted(summary.items()):
            summary_table.add_row(lang, period, str(count))
        
        console.print(summary_table)
        
    except KeyboardInterrupt:
        console.print("\n⚠️  Scraping interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")

if __name__ == "__main__":
    main()
