"""
Utilities Package for GMR Credit Risk Semantic Kernel Orchestration

This package contains utility modules for:
- Template loading and management
- News scraping and aggregation
- Configuration management
- Output path management
"""

from .template_loader import (
    TemplateLoader,
    get_proposal_verification_sections,
    get_company_profile_sections,
    get_financial_analysis_sections,
    get_proposal_verification_instruction,
    get_company_profile_instruction,
    get_financial_analysis_instruction,
    get_market_analyst_instruction,
    get_market_analyst_message
)

from .news_config import (
    SOURCES,
    KEYWORDS_SETS
)

from .news_utils import (
    get_headers,
    is_infrastructure_relevant,
    contains_keywords,
    extract_article_content,
    get_full_content_for_article
)

from .news_scrapers import (
    scrape_with_crawl4ai,
    scrape_with_requests,
    scrape_rss_feed,
    scrape_source_enhanced
)

__all__ = [
    # Template loader
    'TemplateLoader',
    'get_proposal_verification_sections',
    'get_company_profile_sections',
    'get_financial_analysis_sections',
    'get_proposal_verification_instruction',
    'get_company_profile_instruction',
    'get_financial_analysis_instruction',
    'get_market_analyst_instruction',
    'get_market_analyst_message',
    
    # News config
    'SOURCES',
    'KEYWORDS_SETS',
    
    # News utils
    'get_headers',
    'is_infrastructure_relevant',
    'contains_keywords',
    'extract_article_content',
    'get_full_content_for_article',
    
    # News scrapers
    'scrape_with_crawl4ai',
    'scrape_with_requests',
    'scrape_rss_feed',
    'scrape_source_enhanced'
]
