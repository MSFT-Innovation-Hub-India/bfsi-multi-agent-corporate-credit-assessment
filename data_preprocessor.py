"""
GMR Airports Limited Data Preprocessing Pipeline

A production-grade data preprocessing system for financial document analysis.
This module provides comprehensive text cleaning, normalization, intelligent chunking,
and optimization for embedding generation and vector storage.

Key Features:
    - Advanced text normalization and cleaning
    - Context-aware document sectioning
    - Smart chunking with page tracking and overlap
    - Deduplication and content optimization
    - Token-efficient processing for LLM workflows
    - Comprehensive citation generation with page references

Author: Financial Analytics Team
Version: 2.0.0
Date: November 2025
"""

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import tiktoken


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

DEFAULT_ENCODING_MODEL = "cl100k_base"
DEFAULT_MAX_TOKENS = 800
DEFAULT_OVERLAP_TOKENS = 100
CHARS_PER_TOKEN_ESTIMATE = 4

# Input/Output directories
DEFAULT_INPUT_DIR = "extracted_data"
DEFAULT_OUTPUT_DIR = "processed_data"


# ============================================================================
# TOKEN COUNTING AND TEXT UTILITIES
# ============================================================================

def count_tokens(text: str, model: str = DEFAULT_ENCODING_MODEL) -> int:
    """
    Calculate token count for text using tiktoken encoding.
    
    Args:
        text: Input text to tokenize
        model: Encoding model name (default: cl100k_base for GPT-4)
    
    Returns:
        int: Number of tokens in the text
        
    Note:
        Falls back to character-based estimation (1 token ≈ 4 chars) if encoding fails
    """
    if not text:
        return 0
        
    try:
        encoding = tiktoken.get_encoding(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimation using character count
        return len(text) // CHARS_PER_TOKEN_ESTIMATE


def normalize_text(text: str) -> str:
    """
    Normalize and clean text by removing artifacts and standardizing formatting.
    
    Args:
        text: Raw text to normalize
    
    Returns:
        str: Cleaned and normalized text
        
    Normalization steps:
        1. Remove escape characters (\\n, \\t, \\r, quotes)
        2. Standardize currency symbols (Rs., ₹, Crores)
        3. Fix spacing and formatting (camelCase, number-letter boundaries)
        4. Remove excessive punctuation
    """
    if not text:
        return ""
    
    # Step 1: Remove escape characters and fix encoding
    text = text.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')
    text = text.replace('\\"', '"').replace("\\'", "'")
    
    # Step 2: Normalize currency and special symbols
    text = re.sub(r'\\([Rs\.₹])', r'\1', text)  # Fix escaped currency symbols
    text = re.sub(r'Rs\.?\s*Cr\.?', 'Rs. Crores', text)  # Standardize currency
    text = re.sub(r'\\-\\-', '--', text)  # Fix escaped dashes
    text = re.sub(r'\\([%\(\)])', r'\1', text)  # Fix escaped percentages and brackets
    
    # Step 3: Clean up spacing and formatting
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)  # Add space between numbers and letters
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)  # Add space between letters and numbers
    
    # Step 4: Remove excessive punctuation
    text = re.sub(r'[-]{3,}', '---', text)  # Limit consecutive dashes
    text = re.sub(r'[\.]{3,}', '...', text)  # Limit consecutive dots
    
    return text.strip()


# ============================================================================
# CONTENT EXTRACTION
# ============================================================================

def extract_clean_content(data: Dict[str, Any]) -> str:
    """
    Extract and clean text content from document data structure.
    
    Args:
        data: Document data dictionary containing content field
    
    Returns:
        str: Cleaned and normalized text content
    """
    content = data.get("content", "")
    if not content:
        return ""
    
    return normalize_text(content)


def extract_table_content_with_context(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract and format table content with contextual metadata.
    
    Args:
        tables: List of table dictionaries from document intelligence output
    
    Returns:
        List[Dict]: Processed tables with formatted content and context labels
        
    Each processed table includes:
        - table_id: Unique identifier
        - content: Pipe-separated table content
        - context: Categorized table type (Financial Ratios, Balance Sheet, etc.)
        - formatted_content: Ready-to-use string representation
    """
    processed_tables = []
    
    for table_idx, table in enumerate(tables):
        if not table.get("cells"):
            continue
            
        # Group cells by rows for structured formatting
        rows = defaultdict(list)
        for cell in table["cells"]:
            row_idx = cell.get("row_index", 0)
            col_idx = cell.get("column_index", 0)
            content = normalize_text(cell.get("content", ""))
            
            if content.strip():
                rows[row_idx].append((col_idx, content))
        
        # Sort cells in each row by column index
        for row_idx in rows:
            rows[row_idx] = sorted(rows[row_idx], key=lambda x: x[0])
        
        # Format table with headers and rows
        table_lines = []
        headers = []
        
        # Extract headers from first row
        if 0 in rows and rows[0]:
            headers = [cell[1] for cell in rows[0]]
            table_lines.append(" | ".join(headers))
            table_lines.append("-" * len(" | ".join(headers)))
        
        # Extract data rows
        for row_idx in sorted(rows.keys()):
            if row_idx == 0 and headers:  # Skip header row if already processed
                continue
            row_data = [cell[1] for cell in rows[row_idx]]
            if row_data:
                table_lines.append(" | ".join(row_data))
        
        if not table_lines:
            continue
            
        table_content = "\n".join(table_lines)
        
        # Determine table context based on content keywords
        table_context = _classify_table_context(table_content)
        
        processed_tables.append({
            "table_id": table_idx + 1,
            "content": table_content,
            "context": table_context,
            "formatted_content": f"Table {table_idx + 1}: {table_context}\n{table_content}\n"
        })
    
    return processed_tables


def _classify_table_context(table_content: str) -> str:
    """
    Classify table context based on content keywords.
    
    Args:
        table_content: Formatted table content string
    
    Returns:
        str: Classification label for the table
    """
    content_lower = table_content.lower()
    
    # Define classification patterns
    classifications = {
        "Financial Ratios": ["ratio", "percentage", "%", "times"],
        "Balance Sheet": ["balance sheet", "assets", "liabilities", "equity"],
        "Profit & Loss": ["profit", "loss", "income", "revenue", "expenses"],
        "Cash Flow": ["cash flow", "operating", "investing", "financing"],
        "Airport Operations": ["airport", "passenger", "cargo", "aircraft", "movements"],
        "Loan Details": ["loan", "facility", "credit", "borrowing", "repayment"],
        "Credit Rating": ["rating", "grade", "outlook", "credit"]
    }
    
    # Check for keyword matches
    for context, keywords in classifications.items():
        if any(keyword in content_lower for keyword in keywords):
            return context
    
    return "Financial Data"


# ============================================================================
# DEDUPLICATION
# ============================================================================

def deduplicate_content(text_chunks: List[str]) -> List[str]:
    """
    Remove duplicate content using MD5 hash-based deduplication.
    
    Args:
        text_chunks: List of text chunks to deduplicate
    
    Returns:
        List[str]: Unique text chunks preserving original order
        
    Note:
        Uses normalized lowercase comparison for better deduplication accuracy
    """
    seen_hashes: Set[str] = set()
    unique_chunks: List[str] = []
    
    for chunk in text_chunks:
        # Normalize chunk for comparison
        normalized = re.sub(r'\s+', ' ', chunk.lower().strip())
        chunk_hash = hashlib.md5(normalized.encode()).hexdigest()
        
        # Only add if we haven't seen this content before
        if chunk_hash not in seen_hashes:
            seen_hashes.add(chunk_hash)
            unique_chunks.append(chunk)
    
    return unique_chunks


# ============================================================================
# SMART CHUNKING WITH PAGE TRACKING
# ============================================================================

def smart_chunk_text(
    text: str, 
    max_tokens: int = DEFAULT_MAX_TOKENS, 
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS
) -> List[Dict[str, Any]]:
    """
    Intelligently chunk text while preserving semantic boundaries and page tracking.
    
    Args:
        text: Input text to chunk (may contain page/paragraph markers)
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Overlap between consecutive chunks for context continuity
    
    Returns:
        List[Dict]: List of chunk dictionaries with:
            - content: Cleaned chunk text
            - token_count: Number of tokens
            - chunk_id: Sequential identifier (1-based)
            - pages: List of page numbers covered
            - paras: List of (page, para) tuples
            
    Features:
        - Sentence-boundary aware (never cuts mid-sentence)
        - Tracks page numbers from <<PAGE:N>> markers
        - Tracks paragraphs from <<P:page:num>> or <<PARA:page:id>> markers
        - Maintains context overlap between chunks
        - Removes markers from final content
    """
    if not text:
        return []
    
    # Split into sentences while preserving sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks: List[Dict[str, Any]] = []
    
    # Current chunk state
    current_chunk = ""
    current_tokens = 0
    
    # Page and paragraph tracking patterns
    page_pattern = re.compile(r"<<PAGE:(\d+)>>")
    para_pattern = re.compile(r"<<(?:P|PARA):(\d+):(\d+)>>")
    
    # Track pages and paragraphs in current chunk
    chunk_pages: Set[str] = set()
    chunk_paras: List[Tuple[str, str]] = []
    
    def flush_chunk() -> None:
        """Finalize and store the current chunk."""
        nonlocal current_chunk, current_tokens, chunk_pages, chunk_paras
        
        if current_chunk.strip():
            # Remove markers from final content for clean display
            clean_content = re.sub(r'<<(?:PAGE|P|PARA):[^>]+>>\s*', '', current_chunk)
            
            chunks.append({
                "content": clean_content.strip(),
                "token_count": current_tokens,
                "chunk_id": len(chunks) + 1,
                "pages": sorted(list(chunk_pages), key=lambda x: int(x)) if chunk_pages else [],
                "paras": chunk_paras[:] if chunk_paras else []
            })
        
        # Reset state
        current_chunk, current_tokens = "", 0
        chunk_pages.clear()
        chunk_paras.clear()
    
    # Process sentences
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Extract page markers
        for match in page_pattern.finditer(sentence):
            chunk_pages.add(match.group(1))
        
        # Extract paragraph markers
        for match in para_pattern.finditer(sentence):
            chunk_paras.append((match.group(1), match.group(2)))
        
        sentence_tokens = count_tokens(sentence)
        
        # Check if adding this sentence would exceed max tokens
        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            flush_chunk()
            
            # Add overlap from previous chunk if specified
            if overlap_tokens > 0 and chunks:
                overlap_sentences = current_chunk.split('. ')[-2:] if current_chunk else []
                overlap_text = '. '.join(overlap_sentences) + '. ' if overlap_sentences else ''
                overlap_token_count = count_tokens(overlap_text)
                
                if overlap_token_count < overlap_tokens:
                    current_chunk = overlap_text + sentence + ". "
                    current_tokens = overlap_token_count + sentence_tokens
                else:
                    current_chunk = sentence + ". "
                    current_tokens = sentence_tokens
            else:
                current_chunk = sentence + ". "
                current_tokens = sentence_tokens
        else:
            current_chunk += sentence + ". "
            current_tokens += sentence_tokens
    
    # Finalize remaining content
    if current_chunk.strip():
        flush_chunk()
    
    return chunks


# ============================================================================
# DOCUMENT SECTION IDENTIFICATION
# ============================================================================

def identify_document_sections(content: str, filename: str) -> List[Dict[str, Any]]:
    """
    Identify and tag different sections of the document based on content patterns.
    
    Args:
        content: Full document text content
        filename: Document filename for context-specific pattern matching
    
    Returns:
        List[Dict]: List of section dictionaries with:
            - section: Section name/label
            - content: Section text content
            - token_count: Number of tokens in section
            
    Document Types Supported:
        - Board Reports
        - Management Discussion & Analysis (MDA)
        - Corporate Governance Reports
        - Auditor Reports
        - Financial Ratios
        - Loan Proposals
        - Credit Rating Reports
        - GMR Airport Reports
    """
    sections: List[Dict[str, Any]] = []
    
    # Get document-specific patterns
    patterns = _get_section_patterns(filename)
    
    # Split content into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    current_section = "General Content"
    section_content: List[str] = []
    
    # Process paragraphs and identify sections
    for paragraph in paragraphs:
        # Check if paragraph matches any section pattern
        matched_section = None
        for section_name, pattern in patterns.items():
            if re.search(pattern, paragraph, re.IGNORECASE):
                matched_section = section_name
                break
        
        # If we found a new section, save the previous one and start new
        if matched_section and matched_section != current_section:
            if section_content:
                sections.append({
                    "section": current_section,
                    "content": "\n\n".join(section_content),
                    "token_count": count_tokens("\n\n".join(section_content))
                })
            current_section = matched_section
            section_content = [paragraph]
        else:
            section_content.append(paragraph)
    
    # Add final section
    if section_content:
        sections.append({
            "section": current_section,
            "content": "\n\n".join(section_content),
            "token_count": count_tokens("\n\n".join(section_content))
        })
    
    return sections


def _get_section_patterns(filename: str) -> Dict[str, str]:
    """
    Get document-specific section patterns based on filename.
    
    Args:
        filename: Document filename
    
    Returns:
        Dict[str, str]: Mapping of section names to regex patterns
    """
    filename_lower = filename.lower()
    
    # Board Reports
    if "boards_report" in filename_lower:
        return {
            "Company Overview": r"(company\s+overview|about\s+(?:the\s+)?company|business\s+profile)",
            "Board of Directors": r"(board\s+of\s+directors|directors?\s+profile|management\s+team)",
            "Financial Highlights": r"(financial\s+highlights|key\s+financials|financial\s+performance)",
            "Business Operations": r"(operations|business\s+segments|revenue\s+streams)",
            "Assets and Liabilities": r"(assets?\s+and\s+liabilities|balance\s+sheet|financial\s+position)"
        }
    
    # Management Discussion & Analysis
    elif "mda" in filename_lower:
        return {
            "Risk Management": r"(risk\s+management|risk\s+factors|enterprise\s+risk)",
            "Market Analysis": r"(market\s+analysis|industry\s+outlook|competitive\s+landscape)",
            "Financial Analysis": r"(financial\s+analysis|performance\s+review|results\s+of\s+operations)",
            "Future Outlook": r"(outlook|future\s+prospects|forward\s+looking|guidance)"
        }
    
    # Corporate Governance
    elif "governance" in filename_lower:
        return {
            "Corporate Governance": r"(corporate\s+governance|governance\s+framework|compliance)",
            "Board Composition": r"(board\s+composition|director\s+details|board\s+structure)",
            "Audit Information": r"(audit\s+committee|auditor\s+information|internal\s+audit)",
            "Compliance": r"(regulatory\s+compliance|statutory\s+compliance|compliance\s+officer)"
        }
    
    # Auditor Reports
    elif "auditor" in filename_lower:
        return {
            "Auditor's Opinion": r"(auditor'?s?\s+opinion|independent\s+auditor|audit\s+opinion)",
            "Financial Statements": r"(financial\s+statements?|statement\s+of\s+profit|balance\s+sheet)",
            "Notes to Accounts": r"(notes?\s+to\s+(?:the\s+)?(?:financial\s+)?statements?|accounting\s+policies)",
            "Key Audit Matters": r"(key\s+audit\s+matters|critical\s+audit\s+matters|audit\s+findings)"
        }
    
    # Financial Ratios
    elif "ratios" in filename_lower or "financial_ratios" in filename_lower:
        return {
            "Profitability Ratios": r"(profitability\s+ratios|profit\s+margins?|return\s+on)",
            "Liquidity Ratios": r"(liquidity\s+ratios|current\s+ratio|quick\s+ratio)",
            "Efficiency Ratios": r"(efficiency\s+ratios|turnover\s+ratios|management\s+efficiency)",
            "Leverage Ratios": r"(leverage\s+ratios|debt\s+ratios|coverage\s+ratios)"
        }
    
    # GMR Reports
    elif "gmr" in filename_lower:
        return {
            "Business Overview": r"(business\s+overview|company\s+profile|about\s+gmr|gmr\s+airports)",
            "Airport Portfolio": r"(airport\s+portfolio|airport\s+operations|infrastructure|concessions)",
            "Financial Performance": r"(financial\s+performance|revenue|profit|earnings|financial\s+results)",
            "Strategic Initiatives": r"(strategic\s+initiatives|expansion\s+plans|development\s+projects)",
            "Risk Factors": r"(risk\s+factors|business\s+risks|operational\s+risks|regulatory\s+risks)",
            "Regulatory Environment": r"(regulatory\s+environment|aviation\s+regulations|compliance|licensing)"
        }
    
    # Loan Proposals
    elif "loanproposal" in filename_lower or "loan_proposal" in filename_lower:
        return {
            "Borrower Information": r"(borrower\s+information|company\s+details|entity\s+profile|applicant)",
            "Loan Details": r"(loan\s+details|facility\s+details|credit\s+facility|borrowing\s+requirements)",
            "Financial Position": r"(financial\s+position|financial\s+statements|balance\s+sheet|profit\s+loss)",
            "Security and Collateral": r"(security|collateral|guarantee|mortgage|pledge)",
            "Purpose of Loan": r"(purpose\s+of\s+loan|utilization|end\s+use|loan\s+utilization)",
            "Repayment Terms": r"(repayment\s+terms|repayment\s+schedule|tenure|installments)",
            "Risk Assessment": r"(risk\s+assessment|credit\s+risk|business\s+risk|risk\s+mitigation)"
        }
    
    # Credit Rating
    elif "rating" in filename_lower:
        return {
            "Rating Summary": r"(rating\s+summary|credit\s+rating|rating\s+rationale|rating\s+action)",
            "Company Profile": r"(company\s+profile|business\s+profile|entity\s+overview)",
            "Financial Analysis": r"(financial\s+analysis|financial\s+profile|credit\s+profile)",
            "Industry Analysis": r"(industry\s+analysis|sector\s+outlook|industry\s+dynamics)",
            "Rating Outlook": r"(outlook|rating\s+outlook|future\s+prospects|rating\s+stability)"
        }
    
    # Default patterns
    else:
        return {
            "Financial Data": r"(financial|revenue|profit|loss|assets?|liabilities)",
            "Risk Information": r"(risk|uncertainty|contingent|exposure)",
            "Operational Data": r"(operations?|business|performance|results)",
            "Regulatory Information": r"(regulatory|compliance|statutory|legal)",
            "Management Information": r"(management|governance|board|directors)"
        }


# ============================================================================
# DOCUMENT PREPROCESSING
# ============================================================================

def preprocess_document(
    file_path: str, 
    output_dir: str = DEFAULT_OUTPUT_DIR
) -> Dict[str, Any]:
    """
    Preprocess a single document JSON file with comprehensive cleaning and optimization.
    
    Args:
        file_path: Path to input JSON file from document extraction
        output_dir: Directory to save processed output
    
    Returns:
        Dict: Processing result with:
            - success: Boolean indicating success/failure
            - input_file: Source file path
            - output_file: Processed file path
            - original_tokens: Token count before processing
            - processed_tokens: Token count after processing
            - chunks_created: Number of chunks generated
            - sections_identified: Number of document sections found
            
    Processing Pipeline:
        1. Load and validate document
        2. Extract and normalize content
        3. Process tables with context
        4. Identify document sections
        5. Create smart chunks with page tracking
        6. Deduplicate content
        7. Generate metadata and save
    """
    print(f"\n📄 Processing: {Path(file_path).name}")
    
    # Load document data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"   ❌ Error loading file: {e}")
        return {"success": False, "error": str(e)}
    
    filename = Path(file_path).stem
    
    # Step 1: Extract clean content (use marker content if available)
    print("   🧹 Step 1: Extracting clean content...")
    raw_content = data.get("content", "")
    marked_content = data.get("content_marked", "") or raw_content
    
    clean_content = extract_clean_content({"content": marked_content})
    
    if not clean_content:
        print("   ⚠️ No content found in file")
        return {"success": False, "error": "No content found"}
    
    original_tokens = count_tokens(clean_content)
    print(f"   📊 Original content: {len(clean_content):,} chars, ~{original_tokens:,} tokens")
    
    # Step 2: Process tables with context
    print("   📋 Step 2: Processing tables with context...")
    tables = extract_table_content_with_context(data.get("tables", []))
    
    # Step 3: Identify document sections
    print("   🏷️  Step 3: Identifying document sections...")
    sections = identify_document_sections(clean_content, filename)
    
    # Step 4: Smart chunking for each section with page tracking
    print("   ✂️  Step 4: Creating smart chunks with page tracking...")
    all_chunks: List[Dict[str, Any]] = []
    
    for section in sections:
        section_chunks = smart_chunk_text(
            section["content"], 
            max_tokens=DEFAULT_MAX_TOKENS, 
            overlap_tokens=DEFAULT_OVERLAP_TOKENS
        )
        
        # Add section context to chunks
        for chunk in section_chunks:
            chunk["section"] = section["section"]
            chunk["document_type"] = filename
            
            # Format page information for display
            pages_str = ','.join(map(str, chunk.get('pages', []))) if chunk.get('pages') else 'N/A'
            
            chunk["contextual_content"] = (
                f"Document: {filename}\n"
                f"Section: {section['section']}\n"
                f"Pages: {pages_str}\n\n"
                f"Content:\n{chunk['content']}"
            )
            all_chunks.append(chunk)
    
    # Step 5: Add table chunks with context
    print("   📊 Step 5: Adding table chunks...")
    for table in tables:
        table_chunk = {
            "content": table["formatted_content"],
            "token_count": count_tokens(table["formatted_content"]),
            "chunk_id": len(all_chunks) + 1,
            "section": "Financial Tables",
            "document_type": filename,
            "contextual_content": (
                f"Document: {filename}\n"
                f"Section: Financial Tables\n\n"
                f"Content:\n{table['formatted_content']}"
            )
        }
        all_chunks.append(table_chunk)
    
    # Step 6: Deduplicate chunks
    print("   🔄 Step 6: Deduplicating content...")
    unique_contents = deduplicate_content([chunk["content"] for chunk in all_chunks])
    
    # Filter chunks to keep only unique ones
    final_chunks: List[Dict[str, Any]] = []
    seen_contents: Set[str] = set()
    
    for chunk in all_chunks:
        if chunk["content"] in unique_contents and chunk["content"] not in seen_contents:
            seen_contents.add(chunk["content"])
            chunk["chunk_id"] = len(final_chunks) + 1
            
            # Store page coverage metadata
            pages = chunk.get("pages", [])
            chunk["page_start"] = int(pages[0]) if pages else None
            chunk["page_end"] = int(pages[-1]) if pages else None
            chunk["para_coverage"] = chunk.get("paras", [])
            
            final_chunks.append(chunk)
    
    # Step 7: Finalize and save
    print("   ✅ Step 7: Finalizing and saving...")
    total_tokens = sum(chunk["token_count"] for chunk in final_chunks)
    
    processed_data = {
        "document_name": filename,
        "processing_timestamp": datetime.now().isoformat(),
        "original_stats": {
            "content_length": len(clean_content),
            "estimated_tokens": original_tokens,
            "total_pages": data.get("metadata", {}).get("total_pages", 0),
            "total_tables": len(data.get("tables", []))
        },
        "processed_stats": {
            "total_chunks": len(final_chunks),
            "total_tokens": total_tokens,
            "avg_tokens_per_chunk": total_tokens // len(final_chunks) if final_chunks else 0,
            "unique_sections": len(set(chunk["section"] for chunk in final_chunks)),
            "tables_processed": len(tables)
        },
        "sections_identified": list(set(chunk["section"] for chunk in final_chunks)),
        "chunks": final_chunks
    }
    
    # Save processed data
    Path(output_dir).mkdir(exist_ok=True)
    output_file = Path(output_dir) / f"{filename}_processed.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    
    print(f"   💾 Saved to: {output_file}")
    print(f"   📊 Reduced from ~{original_tokens:,} to {total_tokens:,} tokens ({len(final_chunks)} chunks)")
    print(f"   🏷️  Sections: {', '.join(processed_data['sections_identified'])}")
    
    return {
        "success": True,
        "input_file": file_path,
        "output_file": str(output_file),
        "original_tokens": original_tokens,
        "processed_tokens": total_tokens,
        "chunks_created": len(final_chunks),
        "sections_identified": len(processed_data['sections_identified'])
    }


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_all_documents(
    input_dir: str = DEFAULT_INPUT_DIR, 
    output_dir: str = DEFAULT_OUTPUT_DIR
) -> Dict[str, Any]:
    """
    Process all documents in the extracted data directory.
    
    Args:
        input_dir: Directory containing extracted JSON files
        output_dir: Directory to save processed files
    
    Returns:
        Dict: Summary report with:
            - processing_timestamp: ISO timestamp
            - total_files: Total files processed
            - successful_files: Successfully processed count
            - failed_files: Failed processing count
            - total_original_tokens: Total tokens before processing
            - total_processed_tokens: Total tokens after processing
            - token_reduction_percentage: Efficiency gain
            - total_chunks_created: Total chunks generated
            - processing_results: Detailed results per file
    """
    print("🚀 Starting GMR Airports Limited Data Preprocessing Pipeline...")
    print("🎯 Objectives: Clean, normalize, deduplicate, and optimize for embeddings")
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Input directory '{input_dir}' not found")
        return {"success": False, "error": "Input directory not found"}
    
    # Find all JSON files (excluding summary files)
    json_files = [
        f for f in input_path.glob("*.json") 
        if "processing_summary" not in f.name and "preprocessing_summary" not in f.name
    ]
    
    if not json_files:
        print(f"❌ No JSON files found in '{input_dir}'")
        return {"success": False, "error": "No JSON files found"}
    
    print(f"📄 Found {len(json_files)} documents to process:")
    for file_path in json_files:
        print(f"   • {file_path.name}")
    
    # Process each document
    results: List[Dict[str, Any]] = []
    total_original_tokens = 0
    total_processed_tokens = 0
    total_chunks = 0
    
    for file_path in json_files:
        result = preprocess_document(str(file_path), output_dir)
        results.append(result)
        
        if result.get("success"):
            total_original_tokens += result["original_tokens"]
            total_processed_tokens += result["processed_tokens"]
            total_chunks += result["chunks_created"]
    
    # Generate summary report
    successful_files = [r for r in results if r.get("success")]
    failed_files = [r for r in results if not r.get("success")]
    
    token_reduction = (
        ((total_original_tokens - total_processed_tokens) / total_original_tokens * 100) 
        if total_original_tokens > 0 else 0
    )
    
    summary = {
        "processing_timestamp": datetime.now().isoformat(),
        "total_files": len(json_files),
        "successful_files": len(successful_files),
        "failed_files": len(failed_files),
        "total_original_tokens": total_original_tokens,
        "total_processed_tokens": total_processed_tokens,
        "token_reduction_percentage": token_reduction,
        "total_chunks_created": total_chunks,
        "average_tokens_per_chunk": total_processed_tokens // total_chunks if total_chunks > 0 else 0,
        "processing_results": results
    }
    
    # Save summary
    summary_file = Path(output_dir) / "preprocessing_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print final summary
    _print_processing_summary(summary, successful_files, failed_files, summary_file)
    
    return summary


def _print_processing_summary(
    summary: Dict[str, Any],
    successful_files: List[Dict[str, Any]],
    failed_files: List[Dict[str, Any]],
    summary_file: Path
) -> None:
    """Print formatted processing summary to console."""
    print(f"\n{'='*60}")
    print("📋 PREPROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successfully processed: {len(successful_files)} files")
    print(f"❌ Failed to process: {len(failed_files)} files")
    print(f"📊 Token reduction: {summary['total_original_tokens']:,} → {summary['total_processed_tokens']:,} "
          f"({summary['token_reduction_percentage']:.1f}% reduction)")
    print(f"🧩 Total chunks created: {summary['total_chunks_created']:,}")
    print(f"📏 Average tokens per chunk: {summary['average_tokens_per_chunk']:,}")
    
    if successful_files:
        print(f"\n📊 Processed Files Details:")
        for result in successful_files:
            file_name = Path(result["input_file"]).name
            print(f"   📄 {file_name}")
            print(f"      🧩 Chunks: {result['chunks_created']}")
            print(f"      📏 Tokens: {result['original_tokens']:,} → {result['processed_tokens']:,}")
            print(f"      🏷️  Sections: {result['sections_identified']}")
    
    if failed_files:
        print(f"\n❌ Failed Files:")
        for result in failed_files:
            file_name = Path(result.get("input_file", "Unknown")).name
            print(f"   • {file_name}: {result.get('error', 'Unknown error')}")
    
    print(f"\n📋 Summary saved to: {summary_file}")
    print("\n✅ Data preprocessing completed!")
    print("🎯 Ready for embedding generation and vector storage")


# ============================================================================
# CITATION GENERATION
# ============================================================================

def generate_citation(chunk: Dict[str, Any], query_text: str = "") -> str:
    """
    Generate a traceable citation for a chunk with page and paragraph references.
    
    Args:
        chunk: Chunk dictionary containing page and paragraph information
        query_text: Optional text excerpt to include in citation
    
    Returns:
        str: Formatted citation string with source traceability
    
    Example:
        [File: boards_report_processed.json | Section: Financial Highlights | 
         Chunk: 5 | Page 17, Para ~2]
        Total Income = ₹10,835.89 million
    """
    doc_name = chunk.get("document_type", "Unknown")
    section = chunk.get("section", "Unknown Section")
    chunk_id = chunk.get("chunk_id", "?")
    
    # Format page information
    page_start = chunk.get("page_start")
    page_end = chunk.get("page_end")
    
    if page_start and page_end:
        if page_start == page_end:
            page_info = f"Page {page_start}"
        else:
            page_info = f"Pages {page_start}-{page_end}"
    elif page_start:
        page_info = f"Page {page_start}"
    else:
        page_info = "Page N/A"
    
    # Format paragraph information
    para_coverage = chunk.get("para_coverage", [])
    if para_coverage:
        first_para = para_coverage[0][1] if isinstance(para_coverage[0], tuple) else para_coverage[0]
        para_info = f", Para ~{first_para}"
    else:
        para_info = ""
    
    # Build citation
    citation = (
        f"[File: {doc_name}.json | Section: {section} | "
        f"Chunk: {chunk_id} | {page_info}{para_info}]"
    )
    
    if query_text:
        citation += f"\n{query_text}"
    
    return citation


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    """
    Main entry point for the preprocessing pipeline.
    
    Ensures dependencies are installed and executes batch processing.
    """
    try:
        # Verify tiktoken is available
        try:
            import tiktoken
        except ImportError:
            print("📦 Installing tiktoken for token counting...")
            import subprocess
            subprocess.check_call(["pip", "install", "tiktoken"])
            import tiktoken
        
        # Run preprocessing pipeline
        summary = process_all_documents()
        
        # Determine success
        success = (
            summary.get("success") if "success" in summary 
            else summary.get("successful_files", 0) > 0
        )
        
        if success:
            print("\n🎉 Preprocessing pipeline completed successfully!")
            print("📁 Check the 'processed_data' folder for optimized files")
            print("🚀 Ready for Financial Analyst Agent workflow!")
        else:
            print("\n⚠️  Some issues occurred during preprocessing. Check the logs above.")
            
    except Exception as e:
        print(f"\n❌ Error in preprocessing pipeline: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
