"""
Enhanced GMR Airports Limited News Custom Functions for Azure AI Projects
Combines focused scraping + full content extraction for institutional analysis
Multi-category support with deduplication and comprehensive content extraction
Focus: GMR Airports, Infrastructure Sector, Airport Stocks
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
from datetime import datetime, timedelta
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Set, Callable, Any
import logging
import asyncio
import warnings

# Suppress all warnings for clean output
warnings.filterwarnings("ignore")

# Suppress specific asyncio and resource warnings
import sys
if sys.platform == "win32":
    # Suppress Windows-specific asyncio warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    warnings.filterwarnings("ignore", message=".*unclosed transport.*")
    warnings.filterwarnings("ignore", message=".*I/O operation on closed pipe.*")
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Suppress asyncio debug messages  
    import os
    os.environ['PYTHONASYNCIO_DEBUG'] = '0'
    
    # Completely suppress asyncio stderr output during scraping
    import io
    
    class CompleteStderrSuppressor:
        def __init__(self):
            self.original_stderr = sys.stderr
            self.suppressing = False
            
        def write(self, s):
            # Strip whitespace to check content
            stripped = s.strip()
            
            # Suppress empty lines and whitespace-only content during asyncio cleanup
            if not stripped:
                return
                
            # Check if this is asyncio-related garbage (case-insensitive)
            lower_s = s.lower()
            if any(phrase in lower_s for phrase in [
                "exception ignored",
                "traceback",
                "_proactorbasepipetransport",
                "basesubprocesstransport", 
                "unclosed transport",
                "i/o operation on closed pipe",
                "proactor_events.py",
                "base_subprocess.py",
                "windows_utils.py",
                "valueerror:",
                "valueerror",  # Catch standalone ValueError
                "info.append",
                "fd=",
                "fileno()",
                "stdin=",
                "__del__",
                "file \"c:\\users\\", # Catch file paths in tracebacks
                "line 116, in __del__",
                "line 80, in __repr__",
                "line 102, in fileno",
                "line 134, in __del__",
                "line 73, in __repr__"
            ]) or stripped in ["ValueError:", "Traceback (most recent call last):"]:
                # Completely ignore asyncio cleanup noise
                return
            else:
                # Only write legitimate error messages
                self.original_stderr.write(s)
                
        def flush(self):
            self.original_stderr.flush()
    
    # Apply complete stderr suppression for asyncio noise
    sys.stderr = CompleteStderrSuppressor()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Crawl4AI
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
    logger.info("✅ Crawl4AI available for enhanced scraping")
except ImportError:
    CRAWL4AI_AVAILABLE = False
    logger.info("⚠️ Crawl4AI not available, using fallback methods")

# -----------------------
# ENHANCED SOURCES (GMR & Infrastructure focused)
# -----------------------
SOURCES = [
    # Traditional Financial News Sites
    {"name": "Economic Times Markets", "url": "https://economictimes.indiatimes.com/markets/stocks", "method": "beautifulsoup"},
    {"name": "Business Today Markets", "url": "https://www.businesstoday.in/markets", "method": "beautifulsoup"},
    {"name": "Live Mint Markets", "url": "https://www.livemint.com/market", "method": "beautifulsoup"},
    {"name": "Moneycontrol Markets", "url": "https://www.moneycontrol.com/news/business/markets/", "method": "beautifulsoup"},
    {"name": "NDTV Business", "url": "https://www.ndtv.com/business", "method": "beautifulsoup"},
    {"name": "NDTV Profit", "url": "https://www.ndtvprofit.com/", "method": "beautifulsoup"},
    
    # Regional and Additional Sources
    {"name": "Mathrubhumi Business", "url": "https://english.mathrubhumi.com/business", "method": "beautifulsoup", "priority": "high"},
    {"name": "Mathrubhumi Markets", "url": "https://english.mathrubhumi.com/", "method": "crawl4ai"},
    {"name": "Devdiscourse Business", "url": "https://www.devdiscourse.com/business", "method": "beautifulsoup"},
    
    # Infrastructure & Aviation Focused
    {"name": "Financial Express Infrastructure", "url": "https://www.financialexpress.com/infrastructure/", "method": "beautifulsoup"},
    {"name": "Aviation Today India", "url": "https://www.thehindu.com/business/", "method": "beautifulsoup"},
    
    # Company Specific Sources (High Priority)
    {"name": "GMR Group Official Media", "url": "https://www.gmrgroup.in/media/", "method": "crawl4ai", "priority": "high"},
    {"name": "GMR Group Press Releases", "url": "https://www.gmrgroup.in/media/press-releases/", "method": "crawl4ai", "priority": "high"},
    {"name": "GMR Group News Updates", "url": "https://www.gmrgroup.in/media/news-updates/", "method": "crawl4ai", "priority": "high"},
    {"name": "GMR Group Announcements", "url": "https://www.gmrgroup.in/media/announcements/", "method": "crawl4ai", "priority": "high"},
    
    # RSS Feeds
    {"name": "Reuters Infrastructure RSS", "rss": "https://feeds.reuters.com/reuters/INinfrastructure", "method": "rss"},
    {"name": "Business Standard Infrastructure", "rss": "https://www.business-standard.com/rss/industry-infrastructure-102.rss", "method": "rss"},
    
    # Stock Exchange and Analyst Sources
    {"name": "BSE Corporate Announcements", "url": "https://www.bseindia.com/corporates/ann.aspx", "method": "beautifulsoup"},
    {"name": "Infrastructure Sector News", "url": "https://economictimes.indiatimes.com/industry/transportation/airlines-/-aviation", "method": "beautifulsoup"},
    {"name": "ET Infrastructure News", "url": "https://economictimes.indiatimes.com/industry/indl-goods/svs/construction", "method": "beautifulsoup"}
]

# Crawl4AI Configuration
CRAWL4AI_CONFIG = {
    "headless": True,
    "verbose": False,
    "delay_before_return_html": 2.0,
    "timeout": 30
}

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

def get_headers():
    """Enhanced user agent rotation"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }

def is_infrastructure_relevant(text):
    """Enhanced infrastructure/GMR relevance check"""
    text = text.lower()
    infrastructure_indicators = [
        "airport", "aviation", "infrastructure", "gmr", "construction", "project",
        "revenue", "profit", "earnings", "financial", "investment", "development",
        "passenger", "cargo", "operations", "expansion", "announcement", "results",
        "stock", "share", "market", "trading", "valuation", "growth", "contracts"
    ]
    return any(indicator in text for indicator in infrastructure_indicators)

async def scrape_with_crawl4ai(source):
    """Advanced scraping using Crawl4AI for JS-heavy and dynamic sites"""
    if not CRAWL4AI_AVAILABLE:
        logger.warning(f"Crawl4AI not available for {source['name']}, falling back to requests")
        return scrape_with_requests(source)
    
    try:
        logger.info(f"🤖 Using Crawl4AI for {source['name']}...")
        
        async with AsyncWebCrawler(
            headless=CRAWL4AI_CONFIG["headless"],
            verbose=CRAWL4AI_CONFIG["verbose"]
        ) as crawler:
            
            result = await crawler.arun(
                url=source["url"],
                delay_before_return_html=CRAWL4AI_CONFIG["delay_before_return_html"],
                timeout=CRAWL4AI_CONFIG["timeout"]
            )
            
            if result.success:
                # Parse the crawled content
                soup = BeautifulSoup(result.html, "html.parser")
                articles = process_soup_for_articles(soup, source)
                
                # Add metadata from Crawl4AI
                for article in articles:
                    article['scraping_method'] = 'crawl4ai'
                    article['page_title'] = result.metadata.get('title', '')
                    article['crawl_timestamp'] = result.metadata.get('timestamp', '')
                
                logger.info(f"✅ Crawl4AI: Found {len(articles)} articles from {source['name']}")
                return articles
            else:
                logger.error(f"❌ Crawl4AI failed for {source['name']}: {result.error_message}")
                return scrape_with_requests(source)
                
    except Exception as e:
        logger.error(f"❌ Crawl4AI error for {source['name']}: {e}")
        return scrape_with_requests(source)

def scrape_with_requests(source):
    """Traditional requests + BeautifulSoup scraping"""
    try:
        headers = get_headers()
        resp = requests.get(source["url"], headers=headers, timeout=15)
        resp.raise_for_status()
        
        logger.info(f"✅ {source['name']}: Status {resp.status_code}")
        soup = BeautifulSoup(resp.text, "html.parser")
        return process_soup_for_articles(soup, source)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ {source['name']}: {e}")
        return []

def scrape_with_playwright(source):
    """Playwright-based scraping for JS-heavy sites"""
    try:
        # Only import if Playwright is available
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers(get_headers())
            
            # Navigate to page
            page.goto(source["url"], timeout=30000)
            
            # Wait for content to load
            page.wait_for_load_state("networkidle")
            
            # Get page content
            html_content = page.content()
            browser.close()
            
            # Process with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            return process_soup_for_articles(soup, source)
            
    except ImportError:
        logger.warning(f"Playwright not available for {source['name']}, falling back to requests")
        return scrape_with_requests(source)
    except Exception as e:
        logger.error(f"❌ Playwright error for {source['name']}: {e}")
        return []

def process_soup_for_articles(soup, source):
    """Common article processing logic for both methods"""
    articles = []
    seen_hashes = set()

    # Enhanced selectors for better article discovery
    selectors = [
        "a[href*='stocks']", "a[href*='markets']", "a[href*='articleshow']",
        "a[href*='story']", "a[href*='news']", "a[href*='gmr']", "a[href*='infrastructure']",
        "h1 a", "h2 a", "h3 a", ".story-title a", ".headline a", ".title a", ".article-title a",
        ".news-title a", ".content-title a"
    ]
    
    all_links = set()
    for selector in selectors:
        links = soup.select(selector)
        all_links.update(links)
    
    if not all_links:
        all_links = soup.find_all("a", href=True)
    
    logger.info(f"📊 {source['name']}: Processing {len(all_links)} links...")
    
    article_count = 0
    for a in all_links:
        title = a.get_text(strip=True)
        url = a.get("href", "")
        
        if not title or not url or len(title) < 20:
            continue
        
        # Fix relative URLs
        if not url.startswith("http"):
            base_url = "/".join(source["url"].split("/")[:3])
            url = base_url + "/" + url.lstrip("/")
        
        # Create hash for deduplication
        article_hash = hashlib.md5((title + url).encode()).hexdigest()
        if article_hash in seen_hashes:
            continue
        seen_hashes.add(article_hash)
        
        # Check categories
        categories = []
        for category in KEYWORDS_SETS.keys():
            if contains_keywords(title, category):
                categories.append(category)
        
        # Only process if relevant to at least one category
        if not categories:
            continue
        
        # Create article object
        article = {
            "title": title,
            "url": url,
            "source": source["name"],
            "categories": categories,
            "summary": title,  # Will be enhanced with full content
            "extraction_time": datetime.now().isoformat(),
            "hash": article_hash,
            "scraping_method": source.get("method", "beautifulsoup")
        }
        
        articles.append(article)
        article_count += 1
        
        logger.info(f"📰 [{'/'.join(categories)}] {article_count}. {title[:70]}...")
        
        # Limit articles per source for efficiency
        if article_count >= 10:
            break
    
    logger.info(f"✅ {source['name']}: Found {len(articles)} relevant articles")
    return articles

def contains_keywords(text, category):
    """Multi-category keyword matching for GMR and infrastructure"""
    text = text.lower()
    keywords = [k.lower() for k in KEYWORDS_SETS.get(category, [])]
    has_keywords = any(k in text for k in keywords)
    
    # For GMR company, allow direct matches (high priority)
    if category == "gmr_company" and has_keywords:
        return True
    
    # For airport infrastructure, require infrastructure relevance
    if category == "airport_infrastructure" and has_keywords:
        return True
    
    # For other categories, require both keywords AND infrastructure relevance
    if has_keywords and is_infrastructure_relevant(text):
        return True
    
    return False

def extract_article_content(soup, url):
    """Enhanced content extraction for institutional analysis"""
    
    # Site-specific selectors for better content extraction
    selectors_by_site = {
        "economictimes.indiatimes.com": [
            ".Normal", ".article_content", "#pageContent", ".articlebody",
            ".artText", ".story-element-text", ".artSyn", ".story-body"
        ],
        "finance.yahoo.com": [
            ".caas-body", ".article-content", "[data-module='ArticleBody']",
            ".fin-size-large", ".content-wrap", ".content"
        ],
        "businesstoday.in": [
            ".story-content", ".article-body", ".story_content",
            ".arti-content", ".story-element", ".content-area"
        ],
        "livemint.com": [
            ".mainSectionBody", ".paywall", "#storyBody", ".story-content",
            ".FirstEle", ".RightSec", ".story-element"
        ],
        "moneycontrol.com": [
            "#article-main", ".content_wrapper", ".arti-flow",
            ".article_desc", ".article-wrap", ".article-content"
        ],
        "english.mathrubhumi.com": [
            ".article-content", ".story-content", ".news-content", 
            ".content-wrapper", ".article-body", ".story-body",
            ".main-content", ".entry-content"
        ],
        "ndtv.com": [
            ".story-content", ".article-content", ".story-element",
            ".content-wrap", ".news-content", ".article-body"
        ],
        "ndtvprofit.com": [
            ".story-content", ".article-content", ".news-content",
            ".content-area", ".article-body", ".story-body"
        ],
        "devdiscourse.com": [
            ".article-content", ".news-content", ".story-content",
            ".content-wrapper", ".article-body", ".main-content"
        ],
        "financialexpress.com": [
            ".story-content", ".article-content", ".news-content",
            ".content-area", ".article-body", ".story-body"
        ],
        "gmrgroup.in": [
            ".content", ".article-content", ".news-content",
            ".press-release-content", ".media-content", ".main-content"
        ]
    }
    
    # Generic selectors (fallback)
    generic_selectors = [
        "article", ".article-body", ".story-body", ".content", 
        ".post-content", ".entry-content", ".article-content",
        "[role='main']", "main", "#main-content", ".main-content"
    ]
    
    # Determine site-specific selectors
    domain = None
    for site in selectors_by_site.keys():
        if site in url:
            domain = site
            break
    
    selectors = selectors_by_site.get(domain, []) + generic_selectors
    
    # Try each selector
    for selector in selectors:
        try:
            content_div = soup.select_one(selector)
            if content_div:
                # Extract paragraphs and preserve structure
                paragraphs = content_div.find_all(["p", "div"], class_=lambda x: x != "advertisement" if x else True)
                if paragraphs:
                    text_parts = []
                    for p in paragraphs:
                        text = p.get_text().strip()
                        # Filter out ads and navigation elements
                        if text and len(text) > 20 and not any(skip in text.lower() for skip in ["advertisement", "subscribe", "newsletter", "follow us", "read more"]):
                            text_parts.append(text)
                    
                    full_text = " ".join(text_parts)
                    if len(full_text) > 200:  # Ensure substantial content
                        return full_text[:3000]  # Limit for efficiency
        except:
            continue
    
    # Final fallback: all paragraphs on page
    all_paragraphs = soup.find_all("p")
    if all_paragraphs:
        text_parts = [p.get_text().strip() for p in all_paragraphs[:15] if p.get_text().strip() and len(p.get_text().strip()) > 20]
        return " ".join(text_parts)[:3000]
    
    return "Content could not be extracted"

def scrape_rss_feed(url):
    """Enhanced RSS feed processing"""
    try:
        import feedparser
        feed = feedparser.parse(url)
        articles = []
        
        logger.info(f"📡 RSS Feed: Processing {len(feed.entries)} entries")
        
        for entry in feed.entries[:20]:  # Check more entries
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary = entry.get('summary', '')
            published = entry.get('published', None)
            
            # Extract timestamp
            timestamp = None
            if published:
                try:
                    timestamp = datetime(*entry.published_parsed[:6]).isoformat()
                except:
                    timestamp = None
            
            # Create article object
            article = {
                "title": title,
                "url": link,
                "source": "Yahoo Finance RSS",
                "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                "timestamp": timestamp,
                "categories": [],
                "extraction_time": datetime.now().isoformat()
            }
            
            # Check which categories this article belongs to
            full_text = f"{title} {summary}"
            for category in KEYWORDS_SETS.keys():
                if contains_keywords(full_text, category):
                    article['categories'].append(category)
            
            # Only include if it matches at least one category
            if article['categories']:
                articles.append(article)
        
        return articles
    except Exception as e:
        logger.error(f"RSS feed error: {e}")
        return []

def scrape_source_enhanced(source):
    """Enhanced source scraping with hybrid method support including Crawl4AI"""
    try:
        if 'rss' in source:
            print(f"🔍 Scraping RSS feed: {source['name']}")
            return scrape_rss_feed(source['rss'])
        
        # Check if source is disabled
        if source.get('enabled', True) == False:
            print(f"⏭️ Skipping disabled source: {source['name']}")
            return []
        
        # Choose scraping method
        method = source.get('method', 'beautifulsoup')
        
        if method == 'crawl4ai' and CRAWL4AI_AVAILABLE:
            print(f"🤖 Using Crawl4AI for: {source['name']}")
            # Run async function in sync context - fix the event loop issue
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If event loop is already running, use run_until_complete in a thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, scrape_with_crawl4ai(source))
                        return future.result()
                else:
                    return loop.run_until_complete(scrape_with_crawl4ai(source))
            except RuntimeError:
                # Fallback: create new event loop in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, scrape_with_crawl4ai(source))
                    return future.result()
        elif method == 'playwright':
            print(f"🎭 Using Playwright for: {source['name']}")
            return scrape_with_playwright(source)
        else:
            print(f"🌐 Using requests for: {source['name']}")
            return scrape_with_requests(source)
        
    except Exception as e:
        print(f"❌ Error scraping {source['name']}: {e}")
        return []

def get_full_content_for_article(article):
    """Get full content for a single article with enhanced extraction"""
    url = article.get('url', '')
    title = article.get('title', '')
    
    if not url:
        article['full_content'] = "No URL provided"
        article['content_extracted'] = False
        return article
    
    try:        
        headers = get_headers()
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove unwanted elements
        for unwanted in soup(["script", "style", "nav", "header", "footer", "aside", "advertisement"]):
            unwanted.decompose()
        
        # Extract content
        content = extract_article_content(soup, url)
        
        # Clean up content
        content = " ".join(content.split())  # Normalize whitespace
        
        # Update article with full content
        article['full_content'] = content
        article['content_length'] = len(content)
        article['content_extracted'] = True
        
        # Update summary with beginning of content
        if len(content) > 200:
            article['summary'] = content[:200] + "..."
        
        # Add delay to avoid overwhelming servers
        time.sleep(random.uniform(1, 2))
        
    except Exception as e:
        article['full_content'] = f"Content extraction failed: {str(e)}"
        article['content_extracted'] = False
    
    return article

def fetch_gmr_infrastructure_news():
    """
    Enhanced GMR Airports Limited & Infrastructure Sector News Aggregator
    
    FEATURES:
    - Multi-source scraping (GMR Official + Economic Times + Business Today + Live Mint + Moneycontrol + NDTV)
    - Crawl4AI integration for JS-heavy sites and official GMR website
    - Multi-category classification (GMR Company, Airport Infrastructure, Infrastructure Sector, Aviation Sector, Market Index, Competitor Analysis)
    - Full content extraction with site-specific selectors
    - Deduplication using MD5 hashing
    - Concurrent processing for efficiency
    - Enhanced relevance filtering for infrastructure and airport stocks
    
    TARGET: 25-50 unique high-quality articles with full content
    PRIORITY: GMR Company > Airport Infrastructure > Infrastructure Sector > Aviation Sector > Market Index > Competitor Analysis
    
    Returns comprehensive JSON for GMR infrastructure trading analysis and sentiment evaluation
    """
    try:
        logger.info("🚀 ENHANCED GMR INFRASTRUCTURE NEWS AGGREGATOR")
        logger.info("🎯 Features: Multi-source + Crawl4AI + Full Content + Multi-category + Deduplication")
        logger.info("🏗️ Focus: GMR Airports, Infrastructure Sector, Aviation Industry")
        logger.info("=" * 80)
        
        all_articles = {}  # Use hash as key for deduplication
        
        # Step 1: Collect all articles from sources (prioritize GMR official sources)
        high_priority_sources = [s for s in SOURCES if s.get('priority') == 'high']
        regular_sources = [s for s in SOURCES if s.get('priority') != 'high']
        
        # Process high priority sources first (GMR official sites)
        for i, source in enumerate(high_priority_sources):
            print(f"\n🔥 [{i+1}/{len(high_priority_sources)}] HIGH PRIORITY: {source['name']}")
            
            source_articles = scrape_source_enhanced(source)
            
            articles_added = 0
            for article in source_articles:
                article_hash = article.get('hash', hashlib.md5((article['title'] + article['url']).encode()).hexdigest())
                
                if article_hash not in all_articles:
                    article['priority_level'] = 'high'
                    all_articles[article_hash] = article
                    articles_added += 1
                else:
                    # Merge categories if duplicate found
                    existing_categories = set(all_articles[article_hash]['categories'])
                    new_categories = set(article['categories'])
                    all_articles[article_hash]['categories'] = list(existing_categories | new_categories)
            
            print(f"✅ Found {len(source_articles)} articles, added {articles_added} unique")
            
            # Rate limiting between sources
            if i < len(high_priority_sources) - 1:
                print(f"⏱️ Waiting 3-5 seconds before next source...")
                time.sleep(random.uniform(3, 5))
        
        # Process regular sources
        for i, source in enumerate(regular_sources):
            print(f"\n🔍 [{i+1}/{len(regular_sources)}] REGULAR: {source['name']}")
            
            source_articles = scrape_source_enhanced(source)
            
            articles_added = 0
            for article in source_articles:
                article_hash = article.get('hash', hashlib.md5((article['title'] + article['url']).encode()).hexdigest())
                
                if article_hash not in all_articles:
                    article['priority_level'] = 'regular'
                    all_articles[article_hash] = article
                    articles_added += 1
                else:
                    # Merge categories if duplicate found
                    existing_categories = set(all_articles[article_hash]['categories'])
                    new_categories = set(article['categories'])
                    all_articles[article_hash]['categories'] = list(existing_categories | new_categories)
            
            print(f"✅ Found {len(source_articles)} articles, added {articles_added} unique")
            
            # Rate limiting between sources
            if i < len(regular_sources) - 1:
                print(f"⏱️ Waiting 2-4 seconds before next source...")
                time.sleep(random.uniform(2, 4))
        
        articles_list = list(all_articles.values())
        print(f"\n📊 TOTAL: {len(articles_list)} unique articles collected")
        
        # Step 2: Extract full content for articles (prioritize high-priority articles)
        print(f"\n🔄 Extracting full content for analysis...")
        
        # Sort articles by priority (GMR company articles first)
        articles_list.sort(key=lambda x: (
            x.get('priority_level') == 'high',
            'gmr_company' in x.get('categories', []),
            'airport_infrastructure' in x.get('categories', []),
            len(x.get('categories', []))
        ), reverse=True)
        
        # Limit to top 35 most relevant articles for processing
        articles_to_process = articles_list[:35]
        print(f"🎯 Processing top {len(articles_to_process)} most relevant articles")
        
        enhanced_articles = []
        
        if len(articles_to_process) > 8:
            use_threading = True
            max_workers = 3
            print(f"⚡ Using {max_workers} threads for content extraction...")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_article = {executor.submit(get_full_content_for_article, article): article 
                                   for article in articles_to_process}
                
                for future in as_completed(future_to_article):
                    try:
                        enhanced_article = future.result()
                        enhanced_articles.append(enhanced_article)
                        
                        progress = len(enhanced_articles)
                        print(f"� Content extracted: {progress}/{len(articles_to_process)} ({progress/len(articles_to_process)*100:.1f}%)")
                        
                    except Exception as e:
                        print(f"❌ Content extraction error: {e}")
        else:
            print("� Processing sequentially...")
            for i, article in enumerate(articles_to_process, 1):
                enhanced_article = get_full_content_for_article(article)
                enhanced_articles.append(enhanced_article)
                print(f"� Progress: {i}/{len(articles_to_process)} ({i/len(articles_to_process)*100:.1f}%)")
        
        # Step 3: Categorize and prioritize
        categorized_results = {
            "gmr_company": [],
            "airport_infrastructure": [],
            "infrastructure_sector": [],
            "aviation_sector": [],
            "market_index": [],
            "competitor_analysis": []
        }
        
        # Sort articles by category and priority
        for article in enhanced_articles:
            for category in article.get('categories', []):
                if category in categorized_results:
                    categorized_results[category].append(article)
        
        # Calculate statistics
        total_articles = len(enhanced_articles)
        successful_extractions = sum(1 for a in enhanced_articles if a.get('content_extracted', False))
        gmr_specific_count = len(categorized_results["gmr_company"])
        
        # Create comprehensive result
        result = {
            "analysis_type": "gmr_infrastructure_financial_news",
            "company_focus": "GMR Airports Limited (GMRINFRA)",
            "sector_focus": "Infrastructure & Aviation",
            "generation_info": {
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "extraction_date": datetime.now().isoformat(),
                "total_sources_scraped": len(SOURCES),
                "high_priority_sources": len(high_priority_sources),
                "enhancement_features": [
                    "multi_source_scraping", 
                    "crawl4ai_integration",
                    "official_gmr_website_scraping",
                    "full_content_extraction", 
                    "multi_category_classification",
                    "md5_deduplication", 
                    "concurrent_processing",
                    "infrastructure_focus",
                    "priority_based_processing"
                ]
            },
            "summary_stats": {
                "total_unique_articles": total_articles,
                "successful_content_extractions": successful_extractions,
                "content_extraction_rate": f"{successful_extractions/total_articles*100:.1f}%" if total_articles > 0 else "0%",
                "gmr_specific_articles": gmr_specific_count,
                "categories_covered": len([k for k, v in categorized_results.items() if v]),
                "category_breakdown": {k: len(v) for k, v in categorized_results.items()},
                "source_breakdown": {},
                "priority_breakdown": {
                    "high_priority": len([a for a in enhanced_articles if a.get('priority_level') == 'high']),
                    "regular": len([a for a in enhanced_articles if a.get('priority_level') == 'regular'])
                }
            },
            "categorized_articles": categorized_results,
            "all_articles": enhanced_articles,
            "agent_instructions": {
                "sentiment_analysis_focus": [
                    "GMR company specific news and announcements",
                    "Airport infrastructure developments and passenger traffic",
                    "Infrastructure sector trends and competitor analysis",
                    "Financial performance indicators and market sentiment",
                    "Regulatory changes affecting aviation and infrastructure"
                ],
                "key_entities_to_track": [
                    "GMR Group", "GMR Airports", "Delhi Airport (DIAL)", "Hyderabad Airport (GHIAL)",
                    "Adani Airports", "L&T Infrastructure", "Infrastructure sector", "Aviation policy"
                ],
                "sentiment_categories": [
                    "Revenue Growth", "Expansion Plans", "Passenger Traffic", "Regulatory Impact",
                    "Competition", "Financial Health", "Market Position", "Operational Performance"
                ]
            }
        }
        
        # Calculate source breakdown
        for article in enhanced_articles:
            source = article.get('source', 'Unknown')
            if source not in result['summary_stats']['source_breakdown']:
                result['summary_stats']['source_breakdown'][source] = 0
            result['summary_stats']['source_breakdown'][source] += 1
        
        # Save results for reference
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gmr_infrastructure_news_{timestamp}.json"
        
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n🎉 GMR INFRASTRUCTURE NEWS AGGREGATION COMPLETE!")
        logger.info(f"✅ Total unique articles: {total_articles}")
        logger.info(f"✅ GMR specific articles: {gmr_specific_count}")
        logger.info(f"✅ Successful content extractions: {successful_extractions}")
        logger.info(f"✅ Categories covered: {len([k for k, v in categorized_results.items() if v])}")
        logger.info(f"✅ Category breakdown: {result['summary_stats']['category_breakdown']}")
        logger.info(f"✅ Priority breakdown: {result['summary_stats']['priority_breakdown']}")
        logger.info(f"✅ Results saved to: {filename}")
        logger.info(f"✅ Ready for GMR sentiment analysis and trading recommendations!")
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        error_response = {
            "error": f"GMR infrastructure news aggregation failed: {str(e)}",
            "analysis_type": "gmr_infrastructure_financial_news",
            "timestamp": datetime.now().isoformat()
        }
        logger.error(f"❌ Error in GMR aggregation: {e}")
        return json.dumps(error_response, indent=2)
    """
    Enhanced institutional financial news aggregator
    
    FEATURES:
    - Multi-source scraping (Yahoo RSS + Economic Times + Business Today + Live Mint + Moneycontrol)
    - Multi-category classification (Infosys, IT Stocks, Market Index, Tech Stocks, AI News)
    - Full content extraction with site-specific selectors
    - Deduplication using MD5 hashing
    - Concurrent processing for efficiency
    - Enhanced relevance filtering
    
    TARGET: 25-40 unique high-quality articles with full content
    PRIORITY: Infosys > IT Stocks > Market Index > Tech Stocks > AI News
    
    Returns comprehensive JSON for institutional trading analysis
    """
    try:
        logger.info("🚀 ENHANCED INSTITUTIONAL NEWS AGGREGATOR")
        logger.info("🎯 Features: Multi-source + Full Content + Multi-category + Deduplication")
        logger.info("=" * 70)
        
        all_articles = {}  # Use hash as key for deduplication
        
        # Step 1: Collect all articles from sources
        for i, source in enumerate(SOURCES):
            logger.info(f"\n🔍 [{i+1}/{len(SOURCES)}] Scraping {source['name']}...")
            
            source_articles = scrape_source_enhanced(source)
            
            for article in source_articles:
                article_hash = article.get('hash', hashlib.md5((article['title'] + article['url']).encode()).hexdigest())
                
                if article_hash not in all_articles:
                    all_articles[article_hash] = article
                else:
                    # Merge categories if duplicate found
                    existing_categories = set(all_articles[article_hash]['categories'])
                    new_categories = set(article['categories'])
                    all_articles[article_hash]['categories'] = list(existing_categories | new_categories)
            
            # Rate limiting between sources
            if i < len(SOURCES) - 1:
                time.sleep(random.uniform(2, 4))
        
        articles_list = list(all_articles.values())
        logger.info(f"\n📊 Found {len(articles_list)} unique articles across all categories")
        
        # Step 2: Extract full content for articles
        logger.info(f"\n🔄 Extracting full content for institutional analysis...")
        
        # Process articles with threading for efficiency
        enhanced_articles = []
        
        if len(articles_list) > 10:
            use_threading = True
            max_workers = 3
            logger.info(f"🔄 Using {max_workers} threads for content extraction...")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_article = {executor.submit(get_full_content_for_article, article): article 
                                   for article in articles_list}
                
                for future in as_completed(future_to_article):
                    try:
                        enhanced_article = future.result()
                        enhanced_articles.append(enhanced_article)
                        
                        progress = len(enhanced_articles)
                        logger.info(f"📊 Content extraction progress: {progress}/{len(articles_list)} ({progress/len(articles_list)*100:.1f}%)")
                        
                    except Exception as e:
                        logger.error(f"❌ Error in content extraction: {e}")
        else:
            logger.info("🔄 Processing sequentially...")
            for i, article in enumerate(articles_list, 1):
                enhanced_article = get_full_content_for_article(article)
                enhanced_articles.append(enhanced_article)
                logger.info(f"📊 Progress: {i}/{len(articles_list)} ({i/len(articles_list)*100:.1f}%)")
        
        # Step 3: Categorize and prioritize
        categorized_results = {
            "infosys": [],
            "it_stocks": [],
            "market_index": [],
            "tech_stocks": [],
            "ai_news": []
        }
        
        # Sort articles by category
        for article in enhanced_articles:
            for category in article.get('categories', []):
                if category in categorized_results:
                    categorized_results[category].append(article)
        
        # Calculate statistics
        total_articles = len(enhanced_articles)
        successful_extractions = sum(1 for a in enhanced_articles if a.get('content_extracted', False))
        
        # Create comprehensive result
        result = {
            "analysis_type": "enhanced_institutional_financial_news",
            "generation_info": {
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "extraction_date": datetime.now().isoformat(),
                "total_sources_scraped": len(SOURCES),
                "enhancement_features": [
                    "multi_source_scraping", 
                    "full_content_extraction", 
                    "multi_category_classification",
                    "md5_deduplication", 
                    "concurrent_processing",
                    "institutional_focus"
                ]
            },
            "summary_stats": {
                "total_unique_articles": total_articles,
                "successful_content_extractions": successful_extractions,
                "content_extraction_rate": f"{successful_extractions/total_articles*100:.1f}%" if total_articles > 0 else "0%",
                "categories_covered": len([k for k, v in categorized_results.items() if v]),
                "category_breakdown": {k: len(v) for k, v in categorized_results.items()},
                "source_breakdown": {}
            },
            "categorized_articles": categorized_results,
            "all_articles": enhanced_articles
        }
        
        # Calculate source breakdown
        for article in enhanced_articles:
            source = article.get('source', 'Unknown')
            if source not in result['summary_stats']['source_breakdown']:
                result['summary_stats']['source_breakdown'][source] = 0
            result['summary_stats']['source_breakdown'][source] += 1
        
        # Save results for reference
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_institutional_news_{timestamp}.json"
        
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n🎉 ENHANCED INSTITUTIONAL AGGREGATION COMPLETE!")
        logger.info(f"✅ Total unique articles: {total_articles}")
        logger.info(f"✅ Successful content extractions: {successful_extractions}")
        logger.info(f"✅ Categories covered: {len([k for k, v in categorized_results.items() if v])}")
        logger.info(f"✅ Category breakdown: {result['summary_stats']['category_breakdown']}")
        logger.info(f"✅ Results saved to: {filename}")
        logger.info(f"✅ Ready for institutional trading analysis!")
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        error_response = {
            "error": f"Enhanced institutional news aggregation failed: {str(e)}",
            "analysis_type": "enhanced_institutional_financial_news",
            "timestamp": datetime.now().isoformat()
        }
        logger.error(f"❌ Error in enhanced aggregation: {e}")
        return json.dumps(error_response, indent=2)

# Legacy function compatibility
def get_gmr_infrastructure_news():
    """Main function for GMR infrastructure news"""
    return fetch_gmr_infrastructure_news()

def get_infosys_prioritized_ai_tech_stock_news():
    """Legacy compatibility function - redirects to GMR"""
    return fetch_gmr_infrastructure_news()

def get_stock_ai_tech_news():
    """Legacy compatibility function - redirects to GMR"""
    return fetch_gmr_infrastructure_news()

def fetch_institutional_financial_news():
    """Legacy compatibility function - redirects to GMR"""
    return fetch_gmr_infrastructure_news()

def reset_news_cache():
    """Reset cache function for compatibility"""
    return json.dumps({"message": "Cache reset functionality integrated into main function"})

def get_news_cache_info():
    """Cache info function for compatibility"""
    return json.dumps({"message": "Cache info integrated into main function"})

# Define user functions set for Azure AI Projects
user_functions: Set[Callable[..., Any]] = {
    fetch_gmr_infrastructure_news,
    get_gmr_infrastructure_news,
    get_infosys_prioritized_ai_tech_stock_news,
    get_stock_ai_tech_news,
    fetch_institutional_financial_news,
    reset_news_cache,
    get_news_cache_info
}