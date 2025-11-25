"""
News Scraping Utility Functions
Helper functions for web scraping, content extraction, and article processing
"""

import random
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_headers():
    """Generate random user agent headers for web scraping"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }


def is_infrastructure_relevant(text):
    """Check if text is relevant to infrastructure sector"""
    infrastructure_keywords = [
        "infrastructure", "airport", "construction", "highway", "port", 
        "power", "energy", "urban development", "smart city", "transportation",
        "civil engineering", "project", "development", "capex", "infrastructure sector"
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in infrastructure_keywords)


def contains_keywords(text, category, keywords_sets):
    """Check if text contains keywords from a specific category"""
    if category not in keywords_sets:
        return False
    
    text_lower = text.lower()
    keywords = keywords_sets[category]
    
    has_keywords = any(keyword.lower() in text_lower for keyword in keywords)
    
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


def process_soup_for_articles(soup, source, keywords_sets):
    """Process BeautifulSoup object to extract articles"""
    articles = []
    
    # Find article containers
    article_containers = soup.find_all(['article', 'div'], class_=lambda x: x and any(
        term in str(x).lower() for term in ['article', 'story', 'news-item', 'post']
    ))
    
    if not article_containers:
        article_containers = soup.find_all(['div', 'section'], class_=True)
    
    for container in article_containers[:50]:  # Limit to avoid processing too many
        try:
            # Find title
            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a'])
            if not title_elem:
                continue
            
            title = title_elem.get_text().strip()
            
            # Find URL
            link_elem = container.find('a', href=True)
            if not link_elem:
                continue
            
            url = link_elem['href']
            
            # Make URL absolute
            if url.startswith('/'):
                from urllib.parse import urljoin
                url = urljoin(source['url'], url)
            elif not url.startswith('http'):
                continue
            
            # Find summary/description
            summary_elem = container.find(['p', 'div'], class_=lambda x: x and any(
                term in str(x).lower() for term in ['summary', 'description', 'excerpt', 'intro']
            ))
            
            summary = summary_elem.get_text().strip() if summary_elem else ""
            if not summary:
                # Try to get first paragraph
                p_elem = container.find('p')
                summary = p_elem.get_text().strip() if p_elem else title
            
            # Check relevance
            full_text = f"{title} {summary}"
            
            # Categorize
            categories = []
            for category in keywords_sets.keys():
                if contains_keywords(full_text, category, keywords_sets):
                    categories.append(category)
            
            # Only include if matches at least one category
            if categories:
                article = {
                    "title": title,
                    "url": url,
                    "source": source['name'],
                    "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                    "categories": categories,
                    "timestamp": None,
                    "extraction_time": datetime.now().isoformat(),
                    "hash": hashlib.md5((title + url).encode()).hexdigest()
                }
                articles.append(article)
                
        except Exception as e:
            continue
    
    return articles
