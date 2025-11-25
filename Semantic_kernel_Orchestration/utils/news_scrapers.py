"""
News Scraping Methods
Different scraping methods for various website types (BeautifulSoup, Playwright, Crawl4AI, RSS)
"""

import asyncio
import time
import logging
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .news_utils import get_headers, contains_keywords, process_soup_for_articles

logger = logging.getLogger(__name__)

# Try to import Crawl4AI
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    logger.warning("Crawl4AI not available. Install with: pip install crawl4ai")

# Crawl4AI Configuration
CRAWL4AI_CONFIG = {
    "headless": True,
    "verbose": False,
    "delay_before_return_html": 2.0,
    "timeout": 30
}


async def scrape_with_crawl4ai(source):
    """Scrape using Crawl4AI for JavaScript-heavy websites"""
    try:
        async with AsyncWebCrawler(**CRAWL4AI_CONFIG) as crawler:
            result = await crawler.arun(
                url=source['url'],
                bypass_cache=True,
                wait_for_selector="article, .article, .news-item, .story",
                js_code="window.scrollTo(0, document.body.scrollHeight/2);"
            )
            
            if not result.success:
                logger.warning(f"Crawl4AI failed for {source['name']}")
                return []
            
            soup = BeautifulSoup(result.html, "html.parser")
            
            # Import keywords_sets from main module
            from news_customfunction import KEYWORDS_SETS
            articles = process_soup_for_articles(soup, source, KEYWORDS_SETS)
            
            return articles
            
    except Exception as e:
        logger.error(f"Crawl4AI error for {source['name']}: {e}")
        return []


def scrape_with_requests(source):
    """Scrape using requests and BeautifulSoup"""
    try:
        headers = get_headers()
        response = requests.get(source['url'], headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Import keywords_sets from main module
        from news_customfunction import KEYWORDS_SETS
        articles = process_soup_for_articles(soup, source, KEYWORDS_SETS)
        
        return articles
        
    except Exception as e:
        logger.error(f"Requests error for {source['name']}: {e}")
        return []


def scrape_with_playwright(source):
    """Scrape using Playwright for dynamic content"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.goto(source['url'], wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            
            html = page.content()
            browser.close()
            
            soup = BeautifulSoup(html, "html.parser")
            
            # Import keywords_sets from main module
            from news_customfunction import KEYWORDS_SETS
            articles = process_soup_for_articles(soup, source, KEYWORDS_SETS)
            
            return articles
            
    except Exception as e:
        logger.error(f"Playwright error for {source['name']}: {e}")
        return []


def scrape_rss_feed(url):
    """Enhanced RSS feed processing"""
    try:
        import feedparser
        from news_customfunction import KEYWORDS_SETS
        
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
                if contains_keywords(full_text, category, KEYWORDS_SETS):
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
            return scrape_rss_feed(source['rss'])
        
        # Check if source is disabled
        if source.get('enabled', True) == False:
            return []
        
        # Choose scraping method
        method = source.get('method', 'beautifulsoup')
        
        if method == 'crawl4ai' and CRAWL4AI_AVAILABLE:
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
            return scrape_with_playwright(source)
        else:
            return scrape_with_requests(source)
        
    except Exception as e:
        print(f"❌ Error scraping {source['name']}: {e}")
        return []
