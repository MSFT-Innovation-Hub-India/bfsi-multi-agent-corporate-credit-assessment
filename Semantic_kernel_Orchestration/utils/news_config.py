"""
News Scraping Configuration
Source definitions and keyword sets for GMR infrastructure news aggregation
"""

# -----------------------
# ENHANCED SOURCES (GMR & Infrastructure focused)
# -----------------------
SOURCES = [
    {"name": "Yahoo Finance RSS", "rss": "https://feeds.finance.yahoo.com/rss/2.0/headline", "method": "rss"},
    {"name": "Economic Times Markets", "url": "https://economictimes.indiatimes.com/markets/stocks", "method": "beautifulsoup"},
    {"name": "Business Today Markets", "url": "https://www.businesstoday.in/markets", "method": "beautifulsoup"},
    {"name": "Live Mint Markets", "url": "https://www.livemint.com/market", "method": "beautifulsoup"},
    {"name": "Moneycontrol Markets", "url": "https://www.moneycontrol.com/news/business/markets/", "method": "beautifulsoup"},
    {"name": "NDTV Business", "url": "https://www.ndtv.com/business", "method": "beautifulsoup"},
    {"name": "NDTV Profit", "url": "https://www.ndtvprofit.com/", "method": "beautifulsoup"},
    {"name": "Yahoo Finance India", "url": "https://in.finance.yahoo.com/", "method": "beautifulsoup"},
    {"name": "Money9 Business", "url": "https://www.money9.com/category/business", "method": "beautifulsoup"},
    {"name": "Mathrubhumi Business", "url": "https://english.mathrubhumi.com/business", "method": "beautifulsoup", "priority": "high"},
    {"name": "Mathrubhumi Markets", "url": "https://english.mathrubhumi.com/", "method": "crawl4ai"},
    {"name": "Devdiscourse Business", "url": "https://www.devdiscourse.com/business", "method": "beautifulsoup"},
    {"name": "ET Infrastructure", "url": "https://economictimes.indiatimes.com/industry/indl-goods/svs/construction", "method": "beautifulsoup"},
    {"name": "Business Standard Infrastructure", "url": "https://www.business-standard.com/industry/news/infrastructure", "method": "beautifulsoup"},
    {"name": "Financial Express Infrastructure", "url": "https://www.financialexpress.com/infrastructure/", "method": "beautifulsoup"},
    {"name": "Aviation Today India", "url": "https://www.thehindu.com/business/", "method": "beautifulsoup"},
    {"name": "Infrastructure Today", "url": "https://www.infrastructuretoday.co.in/", "method": "beautifulsoup"},
    {"name": "Construction Week", "url": "https://www.constructionweekonline.in/", "method": "beautifulsoup"},
    {"name": "GMR Group Official Media", "url": "https://www.gmrgroup.in/media/", "method": "crawl4ai", "priority": "high"},
    {"name": "GMR Group Press Releases", "url": "https://www.gmrgroup.in/media/press-releases/", "method": "crawl4ai", "priority": "high"},
    {"name": "GMR Group News Updates", "url": "https://www.gmrgroup.in/media/news-updates/", "method": "crawl4ai", "priority": "high"},
    {"name": "GMR Group Announcements", "url": "https://www.gmrgroup.in/media/announcements/", "method": "crawl4ai", "priority": "high"},
    {"name": "NSE Corporate Announcements", "url": "https://www.nseindia.com/companies-listing/corporate-filings-announcements", "method": "beautifulsoup"},
    {"name": "BSE Announcements", "url": "https://www.bseindia.com/markets/MarketInfo/DispNewNoticesCirculars.aspx", "method": "beautifulsoup"},
    {"name": "Reuters Infrastructure RSS", "rss": "https://feeds.reuters.com/reuters/INinfrastructure", "method": "rss"},
    {"name": "Business Standard Infrastructure", "rss": "https://www.business-standard.com/rss/industry-infrastructure-102.rss", "method": "rss"},
    {"name": "NSE India News", "url": "https://www.nseindia.com/", "method": "beautifulsoup"},
    {"name": "BSE India News", "url": "https://www.bseindia.com/", "method": "beautifulsoup"},
    {"name": "BSE Corporate Announcements", "url": "https://www.bseindia.com/corporates/ann.aspx", "method": "beautifulsoup"},
    {"name": "Infrastructure Sector News", "url": "https://economictimes.indiatimes.com/industry/transportation/airlines-/-aviation", "method": "beautifulsoup"},
    {"name": "ET Infrastructure News", "url": "https://economictimes.indiatimes.com/industry/indl-goods/svs/construction", "method": "beautifulsoup"}
]

# -----------------------
# COMPREHENSIVE KEYWORD SETS (GMR & Infrastructure Focus)
# -----------------------
KEYWORDS_SETS = {
    "gmr_company": [
        "GMR", "GMR Group", "GMR Infrastructure", "GMR Airports", "GMR Limited",
        "GMRINFRA", "GMR stock", "GMR shares", "GMR earnings", "GMR results",
        "GMR revenue", "GMR infrastructure limited", "gmr group", "gmr airports limited"
    ],
    "airport_infrastructure": [
        "Delhi Airport", "DIAL", "Hyderabad Airport", "GHIAL", "Rajiv Gandhi International Airport",
        "Indira Gandhi International Airport", "airport infrastructure", "aviation infrastructure",
        "airport operations", "passenger traffic", "cargo operations", "airport revenue",
        "duty free", "airport retail", "aeronautical revenue", "non-aeronautical revenue"
    ],
    "infrastructure_sector": [
        "infrastructure", "infrastructure sector", "infrastructure stocks", "Nifty Infrastructure",
        "power projects", "energy infrastructure", "transportation infrastructure",
        "highways", "airports", "ports", "urban infrastructure", "smart cities",
        "L&T", "Larsen & Toubro", "Adani", "Adani Group", "infrastructure development"
    ],
    "aviation_sector": [
        "aviation", "aviation sector", "airline industry", "air traffic", "aviation stocks",
        "IndiGo", "SpiceJet", "Air India", "Vistara", "civil aviation", "DGCA",
        "aviation policy", "flight operations", "aircraft", "airline passenger"
    ],
    "market_index": [
        "Nifty 50", "Sensex", "Nifty", "BSE Sensex", "NSE", "market index",
        "benchmark index", "Nifty Infrastructure", "Nifty PSU Bank", "index performance",
        "stock market", "equity market", "market movement", "market analysis"
    ],
    "competitor_analysis": [
        "Adani Airports", "Adani Group", "L&T", "Larsen & Toubro", "IRB Infrastructure",
        "Dilip Buildcon", "KNR Constructions", "PNC Infratech", "infrastructure companies",
        "airport operators", "private airports", "AAI", "Airports Authority of India"
    ]
}
