#!/usr/bin/env python3
"""
GitHub Trending Developers Web Crawler
Scrapes trending developers from GitHub and saves to CSV and JSON
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
import os
from rich.console import Console
from rich.progress import track
from rich.panel import Panel
from rich.table import Table

GITHUB_URL = "https://github.com/trending/developers"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
OUTPUT_DIR = "data"

def setup_directories():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def scrape_trending_developers():
    console = Console()
    console.print(Panel("🚀 GitHub Trending Developers Scraper", style="bold blue"))
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        console.print("📡 Fetching GitHub trending page...")
        response = requests.get(GITHUB_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        developers = []
        
        developer_elements = soup.find_all('article', class_='Box-row')
        console.print(f"🔍 Found {len(developer_elements)} developers to parse")
        
        for i, element in enumerate(track(developer_elements, description="Parsing developers...")):
            try:
                developer = {'rank': i + 1}
                
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
                console.print(f"⚠️  Error parsing developer {i+1}: {e}", style="yellow")
                continue
        
        return developers
        
    except requests.RequestException as e:
        console.print(f"❌ Error fetching data: {e}", style="red")
        return []
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        return []

def save_to_csv(developers, filename):
    if not developers:
        return False
    
    fieldnames = ['rank', 'username', 'name', 'repo_description', 'avatar_url', 'profile_url', 'popular_repo', 'scraped_at']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(developers)
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def save_to_json(developers, filename):
    if not developers:
        return False
    
    data = {
        'scraped_at': datetime.now().isoformat(),
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
    table.add_column("Popular Repo", style="yellow", width=25)
    table.add_column("Repo Desc", style="blue", width=30)
    
    for dev in developers[:10]:
        table.add_row(
            str(dev['rank']),
            dev['username'][:18] + "..." if len(dev['username']) > 18 else dev['username'],
            dev['name'][:23] + "..." if len(dev['name']) > 23 else dev['name'],
            dev['popular_repo'][:23] + "..." if len(dev['popular_repo']) > 23 else dev['popular_repo'],
            dev['repo_description'][:28] + "..." if len(dev['repo_description']) > 28 else dev['repo_description']
        )
    
    console.print(table)
    
    if len(developers) > 10:
        console.print(f"\n... and {len(developers) - 10} more developers", style="dim")

def main():
    console = Console()
    
    try:
        setup_directories()
        developers = scrape_trending_developers()
        
        if not developers:
            console.print("❌ No data scraped", style="red")
            return
        
        timestamp = get_timestamp()
        csv_filename = os.path.join(OUTPUT_DIR, f"github_trending_developers_{timestamp}.csv")
        json_filename = os.path.join(OUTPUT_DIR, f"github_trending_developers_{timestamp}.json")
        
        console.print("\n💾 Saving data...")
        
        csv_saved = save_to_csv(developers, csv_filename)
        json_saved = save_to_json(developers, json_filename)
        
        console.print("\n" + "="*60)
        display_results(developers)
        
        console.print(f"\n✅ Successfully scraped {len(developers)} developers!", style="bold green")
        
        if csv_saved:
            console.print(f"📄 CSV saved: {csv_filename}", style="green")
        if json_saved:
            console.print(f"📄 JSON saved: {json_filename}", style="green")
            
        if not csv_saved or not json_saved:
            console.print("⚠️  Some files failed to save", style="yellow")
        
    except KeyboardInterrupt:
        console.print("\n⚠️  Scraping interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")

if __name__ == "__main__":
    main()
