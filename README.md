# GitHub Trending Developers Web Crawler

## 📋 Project Overview
This web crawler scrapes trending developers from GitHub's trending page and saves the data in both CSV and JSON formats with a beautiful command-line interface.

## 🎯 Objective
Track trending developers on GitHub to identify popular contributors and technology trends.

## 📁 Project Structure
```
WebCrawler/
├── README.md
├── requirements.txt
├── main.py
├── data/
│   ├── *.csv
│   └── *.json
└── LICENSE
```

##  Installation

```bash
pip install -r requirements.txt
```

## 🎮 Usage

```bash
python main.py
```

## 📊 Data Fields
- **rank**: Position in trending list
- **name**: Developer's full name
- **username**: GitHub username
- **avatar_url**: Profile picture URL
- **profile_url**: GitHub profile link
- **popular_repo**: Trending repository name
- **repo_description**: Repository description
- **scraped_at**: Timestamp

## 📁 Output Files
- `data/github_trending_developers_YYYYMMDD_HHMMSS.csv`
- `data/github_trending_developers_YYYYMMDD_HHMMSS.json`

## 📋 Requirements
- Python 3.6+
- requests
- beautifulsoup4
- rich

##  License
MIT License