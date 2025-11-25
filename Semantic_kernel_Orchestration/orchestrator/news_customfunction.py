"""
GMR Airports Limited News Custom Functions
Features: Multi-source scraping, full content extraction, multi-category classification
Focus: GMR Airports, Infrastructure Sector, Airport Stocks
"""

import time
import random
import json
from datetime import datetime
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Set, Callable, Any
import logging
import warnings

# Import utilities from utils package
from utils.news_config import SOURCES, KEYWORDS_SETS
from utils.news_utils import get_headers, is_infrastructure_relevant, contains_keywords, extract_article_content, get_full_content_for_article
from utils.news_scrapers import (
    CRAWL4AI_CONFIG,
    scrape_with_crawl4ai, 
    scrape_with_requests, 
    scrape_rss_feed,
    scrape_source_enhanced
)

# Suppress warnings for clean output
warnings.filterwarnings("ignore")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# MAIN AGGREGATION FUNCTION
# =============================================================================

def fetch_gmr_infrastructure_news():
    """
    GMR Airports Limited & Infrastructure Sector News Aggregator
    
    Features:
    - Multi-source scraping with Crawl4AI integration
    - Multi-category classification with deduplication
    - Full content extraction with concurrent processing
    - Priority: GMR Company > Airport Infrastructure > Infrastructure Sector
    
    Returns: Comprehensive JSON for sentiment analysis and trading recommendations
    """
    try:
        logger.info("GMR Infrastructure News Aggregator - Starting")
        
        all_articles = {}
        
        # Collect articles from sources (prioritize GMR official sources)
        high_priority_sources = [s for s in SOURCES if s.get('priority') == 'high']
        regular_sources = [s for s in SOURCES if s.get('priority') != 'high']
        
        # Process high priority sources first
        for i, source in enumerate(high_priority_sources):
            source_articles = scrape_source_enhanced(source)
            
            for article in source_articles:
                article_hash = article.get('hash', hashlib.md5((article['title'] + article['url']).encode()).hexdigest())
                
                if article_hash not in all_articles:
                    article['priority_level'] = 'high'
                    all_articles[article_hash] = article
                else:
                    # Merge categories if duplicate
                    existing = set(all_articles[article_hash]['categories'])
                    all_articles[article_hash]['categories'] = list(existing | set(article['categories']))
            
            # Rate limiting between sources
            if i < len(high_priority_sources) - 1:
                time.sleep(random.uniform(3, 5))
        
        # Process regular sources
        for i, source in enumerate(regular_sources):
            source_articles = scrape_source_enhanced(source)
            
            for article in source_articles:
                article_hash = article.get('hash', hashlib.md5((article['title'] + article['url']).encode()).hexdigest())
                
                if article_hash not in all_articles:
                    article['priority_level'] = 'regular'
                    all_articles[article_hash] = article
                else:
                    # Merge categories if duplicate
                    existing = set(all_articles[article_hash]['categories'])
                    all_articles[article_hash]['categories'] = list(existing | set(article['categories']))
            
            # Rate limiting between sources
            if i < len(regular_sources) - 1:
                time.sleep(random.uniform(2, 4))
        
        articles_list = list(all_articles.values())
        
        # Sort and extract full content from articles
        articles_list.sort(key=lambda x: (
            x.get('priority_level') == 'high',
            'gmr_company' in x.get('categories', []),
            'airport_infrastructure' in x.get('categories', []),
            len(x.get('categories', []))
        ), reverse=True)
        
        # Limit to top 35 most relevant articles for processing
        articles_to_process = articles_list[:35]
        
        enhanced_articles = []
        
        if len(articles_to_process) > 8:
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_article = {executor.submit(get_full_content_for_article, article): article 
                                   for article in articles_to_process}
                
                for future in as_completed(future_to_article):
                    try:
                        enhanced_article = future.result()
                        enhanced_articles.append(enhanced_article)
                    except Exception as e:
                        logger.warning(f"Content extraction error: {e}")
        else:
            for article in articles_to_process:
                enhanced_articles.append(get_full_content_for_article(article))
        
        # Categorize articles
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
        
        # Create simplified result for agent
        result = {
            "timestamp": datetime.now().isoformat(),
            "total_articles": len(enhanced_articles),
            "categorized_articles": categorized_results,
            "all_articles": enhanced_articles
        }
        
        logger.info(f"Aggregation complete: {len(enhanced_articles)} articles")
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        error_response = {
            "error": f"GMR infrastructure news aggregation failed: {str(e)}",
            "analysis_type": "gmr_infrastructure_financial_news",
            "timestamp": datetime.now().isoformat()
        }
        logger.error(f"Error in GMR aggregation: {e}")
        return json.dumps(error_response, indent=2)

# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================

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

# =============================================================================
# AZURE AI PROJECTS USER FUNCTIONS SET
# =============================================================================

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
