"""
GMR Airports Limited Document Intelligence Extractor

Production-grade document extraction system for financial documents using Azure Document Intelligence.
Processes PDFs from Azure Blob Storage or local files, extracting structured content including
text, tables, and metadata with page-level tracking.

Features:
    - Azure Blob Storage integration with SAS token generation
    - Local file processing fallback
    - Comprehensive content extraction (text, tables, paragraphs)
    - Page and paragraph tracking with markers
    - Batch processing with error handling
    - JSON output with structured metadata

Author: Financial Analytics Team
Version: 2.0.0
"""

import base64
import json
import string
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas
from dotenv import load_dotenv

from config import (
    BLOB_CONTAINER_NAME,
    DOC_INTEL_ENDPOINT,
    DOC_INTEL_KEY,
    STORAGE_ACCOUNT_KEY,
    STORAGE_ACCOUNT_NAME,
)

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Initialize Azure clients
document_client = DocumentIntelligenceClient(
    endpoint=DOC_INTEL_ENDPOINT,
    credential=AzureKeyCredential(DOC_INTEL_KEY)
)

# Constants
OUTPUT_DIR = "extracted_data"
ALLOWED_FILENAME_CHARS = set(string.ascii_letters + string.digits + '_-=')
SAS_TOKEN_EXPIRY_HOURS = 1
RATE_LIMIT_DELAY_SECONDS = 2
MAX_CHUNK_CHARS = 2000  # ~500 tokens


# ============================================================================
# SERIALIZATION UTILITIES
# ============================================================================

def serialize_bounding_region(obj: Any) -> Any:
    """
    Convert Azure Document Intelligence objects to JSON-serializable format.
    
    Args:
        obj: Azure DI object (can be complex nested structure)
    
    Returns:
        JSON-serializable representation
    """
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, list):
                result[key] = [serialize_bounding_region(item) for item in value]
            elif hasattr(value, '__dict__'):
                result[key] = serialize_bounding_region(value)
            elif isinstance(value, (str, int, float, bool, type(None))):
                result[key] = value
            else:
                result[key] = str(value)
        return result
    elif isinstance(obj, list):
        return [serialize_bounding_region(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj)


def clean_filename_for_key(filename: str) -> str:
    """
    Sanitize filename for use as document key.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename (base64 encoded if contains special characters)
    """
    clean = filename.replace('.', '_').replace('-', '_').replace(' ', '_')
    
    if any(c not in ALLOWED_FILENAME_CHARS for c in clean):
        return base64.urlsafe_b64encode(filename.encode()).decode()
    
    return clean


# ============================================================================
# AZURE BLOB STORAGE OPERATIONS
# ============================================================================

def get_blob_service_client() -> Optional[BlobServiceClient]:
    """Create and return Azure Blob Service Client."""
    try:
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={STORAGE_ACCOUNT_NAME};"
            f"AccountKey={STORAGE_ACCOUNT_KEY};"
            f"EndpointSuffix=core.windows.net"
        )
        return BlobServiceClient.from_connection_string(connection_string)
    except Exception as e:
        print(f"Error connecting to blob storage: {e}")
        return None


def get_all_blobs_from_container() -> List[str]:
    """
    Retrieve all PDF blob names from configured container.
    
    Returns:
        List of PDF blob names
    """
    blob_service_client = get_blob_service_client()
    if not blob_service_client:
        return []
    
    try:
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        blobs = container_client.list_blobs()
        return [blob.name for blob in blobs if blob.name.lower().endswith('.pdf')]
    except Exception as e:
        print(f"Error listing blobs: {e}")
        return []


def generate_sas_url(file_name: str) -> Optional[str]:
    """
    Generate SAS URL for blob access.
    
    Args:
        file_name: Blob name
    
    Returns:
        SAS URL with read permissions
    """
    try:
        sas_token = generate_blob_sas(
            account_name=STORAGE_ACCOUNT_NAME,
            container_name=BLOB_CONTAINER_NAME,
            blob_name=file_name,
            account_key=STORAGE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=SAS_TOKEN_EXPIRY_HOURS)
        )
        return f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{BLOB_CONTAINER_NAME}/{file_name}?{sas_token}"
    except Exception as e:
        print(f"Error generating SAS URL for {file_name}: {e}")
        return None


# ============================================================================
# DOCUMENT INTELLIGENCE PROCESSING
# ============================================================================

def analyze_document_from_url(blob_url: str) -> Optional[Any]:
    """
    Analyze document using Azure Document Intelligence from URL.
    
    Args:
        blob_url: SAS URL to PDF document
    
    Returns:
        Analysis result or None on failure
    """
    try:
        poller = document_client.begin_analyze_document(
            "prebuilt-layout", 
            {"urlSource": blob_url}
        )
        return poller.result()
    except Exception as e:
        print(f"Error analyzing document: {e}")
        return None


def analyze_document_from_bytes(file_content: bytes) -> Optional[Any]:
    """
    Analyze document using Azure Document Intelligence from bytes.
    
    Args:
        file_content: PDF file content as bytes
    
    Returns:
        Analysis result or None on failure
    """
    try:
        poller = document_client.begin_analyze_document(
            "prebuilt-layout",
            {"base64Source": base64.b64encode(file_content).decode()}
        )
        return poller.result()
    except Exception as e:
        print(f"Error analyzing document: {e}")
        return None


def extract_comprehensive_data(result: Any) -> Dict[str, Any]:
    """
    Extract structured data from Document Intelligence result.
    
    Args:
        result: Azure DI analysis result
    
    Returns:
        Structured data dictionary with content, pages, tables, paragraphs, and metadata
    """
    extracted_data = {
        "content": "",
        "pages": [],
        "tables": [],
        "paragraphs": [],
        "metadata": {
            "total_pages": 0,
            "extraction_timestamp": datetime.now().isoformat(),
            "document_type": "financial_report"
        }
    }
    
    if not result:
        return extracted_data
    
    try:
        # Extract page-level content
        if hasattr(result, 'pages'):
            extracted_data["metadata"]["total_pages"] = len(result.pages)
            
            for page_idx, page in enumerate(result.pages):
                page_data = {
                    "page_number": page_idx + 1,
                    "content": "",
                    "lines": [],
                    "words": []
                }
                
                if hasattr(page, 'lines'):
                    for line in page.lines:
                        line_content = line.content
                        page_data["lines"].append({
                            "content": line_content,
                            "bounding_box": serialize_bounding_region(line.polygon) if hasattr(line, 'polygon') and line.polygon else None
                        })
                        page_data["content"] += line_content + " "
                        extracted_data["content"] += line_content + " "
                
                if hasattr(page, 'words'):
                    for word in page.words:
                        page_data["words"].append({
                            "content": word.content,
                            "confidence": word.confidence if hasattr(word, 'confidence') else None,
                            "bounding_box": serialize_bounding_region(word.polygon) if hasattr(word, 'polygon') and word.polygon else None
                        })
                
                extracted_data["pages"].append(page_data)
        
        # Extract tables
        if hasattr(result, 'tables'):
            for table_idx, table in enumerate(result.tables):
                table_data = {
                    "table_id": table_idx,
                    "row_count": getattr(table, 'row_count', 0),
                    "column_count": getattr(table, 'column_count', 0),
                    "cells": [],
                    "content": ""
                }
                
                if hasattr(table, 'cells'):
                    for cell in table.cells:
                        cell_data = {
                            "content": cell.content,
                            "row_index": getattr(cell, 'row_index', None),
                            "column_index": getattr(cell, 'column_index', None),
                            "kind": getattr(cell, 'kind', None)
                        }
                        table_data["cells"].append(cell_data)
                        table_data["content"] += cell.content + " "
                
                extracted_data["tables"].append(table_data)
                extracted_data["content"] += table_data["content"] + " "
        
        # Extract paragraphs with page numbers
        if hasattr(result, 'paragraphs'):
            for para_idx, paragraph in enumerate(result.paragraphs):
                page_no = None
                if getattr(paragraph, 'bounding_regions', None):
                    try:
                        page_no = paragraph.bounding_regions[0].page_number
                    except Exception:
                        pass
                
                para_data = {
                    "paragraph_id": para_idx + 1,
                    "content": paragraph.content,
                    "role": getattr(paragraph, 'role', None),
                    "page_number": page_no,
                    "bounding_regions": serialize_bounding_region(paragraph.bounding_regions) if hasattr(paragraph, 'bounding_regions') and paragraph.bounding_regions else None
                }
                extracted_data["paragraphs"].append(para_data)
        
        # Build page-marked content for preprocessing
        master_with_markers = []
        for p in extracted_data["pages"]:
            pg = p["page_number"]
            master_with_markers.append(f"<<PAGE:{pg}>>")
            for li, line in enumerate(p["lines"], start=1):
                master_with_markers.append(f"<<P:{pg}:{li}>> {line['content']}")
        
        for para in extracted_data["paragraphs"]:
            if para.get("page_number") and para.get("content"):
                master_with_markers.append(
                    f"<<PARA:{para['page_number']}:{para['paragraph_id']}>> {para['content']}"
                )
        
        extracted_data["content_marked"] = "\n".join(master_with_markers)
        extracted_data["content"] = extracted_data["content"].strip()
        
    except Exception as e:
        print(f"Error during data extraction: {e}")
    
    return extracted_data


def chunk_text(text: str, max_tokens: int = 500) -> List[str]:
    """
    Split text into chunks for vectorization.
    
    Args:
        text: Input text
        max_tokens: Maximum tokens per chunk (approximated as chars/4)
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    max_chars = max_tokens * 4
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + '. '
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def save_extracted_data(
    file_name: str, 
    extracted_data: Dict[str, Any], 
    output_dir: str = OUTPUT_DIR
) -> Optional[str]:
    """
    Save extracted data to JSON file.
    
    Args:
        file_name: Source filename
        extracted_data: Extracted data dictionary
        output_dir: Output directory
    
    Returns:
        Output file path or None on failure
    """
    try:
        Path(output_dir).mkdir(exist_ok=True)
        
        base_name = Path(file_name).stem
        output_file = Path(output_dir) / f"{base_name}.json"
        
        # Add metadata
        extracted_data["metadata"]["source_file"] = file_name
        extracted_data["metadata"]["processing_timestamp"] = datetime.now().isoformat()
        extracted_data["metadata"]["content_length"] = len(extracted_data["content"])
        extracted_data["metadata"]["total_tables"] = len(extracted_data["tables"])
        extracted_data["metadata"]["total_paragraphs"] = len(extracted_data["paragraphs"])
        
        # Create chunks
        extracted_data["text_chunks"] = chunk_text(extracted_data["content"])
        extracted_data["metadata"]["total_chunks"] = len(extracted_data["text_chunks"])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
        
    except Exception as e:
        print(f"Error saving extracted data: {e}")
        return None


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_configuration() -> bool:
    """
    Validate configuration and determine processing mode.
    
    Returns:
        True if configuration is valid or local files are available
    """
    data_folder = Path("DATA")
    if data_folder.exists() and list(data_folder.glob("*.pdf")):
        return True
    
    required_vars = [
        STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY, BLOB_CONTAINER_NAME,
        DOC_INTEL_ENDPOINT, DOC_INTEL_KEY
    ]
    
    if any(not var for var in required_vars):
        print("Warning: Missing cloud configuration. Will process local files if available.")
        return True
    
    return True


# ============================================================================
# FILE PROCESSING
# ============================================================================

def process_local_files() -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Process local PDF files from DATA folder.
    
    Returns:
        Tuple of (processed_files, failed_files)
    """
    data_folder = Path("DATA")
    if not data_folder.exists():
        return [], []
    
    pdf_files = list(data_folder.glob("*.pdf"))
    if not pdf_files:
        return [], []
    
    print(f"Processing {len(pdf_files)} local PDF files...")
    
    processed_files = []
    failed_files = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        
        try:
            with open(pdf_file, 'rb') as f:
                file_content = f.read()
            
            result = analyze_document_from_bytes(file_content)
            if not result:
                failed_files.append(pdf_file.name)
                continue
            
            extracted_data = extract_comprehensive_data(result)
            
            if not extracted_data["content"].strip():
                print(f"Warning: No content extracted from {pdf_file.name}")
                failed_files.append(pdf_file.name)
                continue
            
            output_file = save_extracted_data(pdf_file.name, extracted_data)
            if output_file:
                processed_files.append({
                    "source_file": pdf_file.name,
                    "output_file": output_file,
                    "content_length": len(extracted_data["content"]),
                    "pages": extracted_data["metadata"]["total_pages"],
                    "tables": extracted_data["metadata"]["total_tables"],
                    "chunks": extracted_data["metadata"]["total_chunks"]
                })
            else:
                failed_files.append(pdf_file.name)
            
            time.sleep(RATE_LIMIT_DELAY_SECONDS)
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")
            failed_files.append(pdf_file.name)
    
    return processed_files, failed_files


def process_blob_files(file_names: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Process PDF files from Azure Blob Storage.
    
    Args:
        file_names: List of blob names to process
    
    Returns:
        Tuple of (processed_files, failed_files)
    """
    processed_files = []
    failed_files = []
    
    for i, file_name in enumerate(file_names, 1):
        print(f"[{i}/{len(file_names)}] Processing: {file_name}")
        
        try:
            blob_url = generate_sas_url(file_name)
            if not blob_url:
                failed_files.append(file_name)
                continue
            
            result = analyze_document_from_url(blob_url)
            if not result:
                failed_files.append(file_name)
                continue
            
            extracted_data = extract_comprehensive_data(result)
            
            if not extracted_data["content"].strip():
                print(f"Warning: No content extracted from {file_name}")
                failed_files.append(file_name)
                continue
            
            output_file = save_extracted_data(file_name, extracted_data)
            if output_file:
                processed_files.append({
                    "source_file": file_name,
                    "output_file": output_file,
                    "content_length": len(extracted_data["content"]),
                    "pages": extracted_data["metadata"]["total_pages"],
                    "tables": extracted_data["metadata"]["total_tables"],
                    "chunks": extracted_data["metadata"]["total_chunks"]
                })
            else:
                failed_files.append(file_name)
            
            time.sleep(RATE_LIMIT_DELAY_SECONDS)
            
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            failed_files.append(file_name)
    
    return processed_files, failed_files


def save_summary_report(
    processed_files: List[Dict[str, Any]], 
    failed_files: List[str],
    processing_mode: str = "cloud"
) -> None:
    """
    Save processing summary report.
    
    Args:
        processed_files: List of successfully processed files
        failed_files: List of failed file names
        processing_mode: 'cloud' or 'local_files'
    """
    summary_report = {
        "processing_timestamp": datetime.now().isoformat(),
        "processing_mode": processing_mode,
        "total_files": len(processed_files) + len(failed_files),
        "processed_successfully": len(processed_files),
        "failed_files": len(failed_files),
        "processed_files": processed_files,
        "failed_file_names": failed_files,
        "total_content_length": sum(f["content_length"] for f in processed_files),
        "total_pages": sum(f["pages"] for f in processed_files),
        "total_tables": sum(f["tables"] for f in processed_files),
        "total_chunks": sum(f["chunks"] for f in processed_files)
    }
    
    try:
        Path(OUTPUT_DIR).mkdir(exist_ok=True)
        with open(f"{OUTPUT_DIR}/processing_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not save summary report: {e}")


def print_summary(processed_files: List[Dict[str, Any]], failed_files: List[str]) -> None:
    """Print processing summary."""
    print(f"\n{'='*60}")
    print("PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Successfully processed: {len(processed_files)} files")
    print(f"Failed: {len(failed_files)} files")
    
    if processed_files:
        total_pages = sum(f["pages"] for f in processed_files)
        total_tables = sum(f["tables"] for f in processed_files)
        print(f"Total pages: {total_pages}")
        print(f"Total tables: {total_tables}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main() -> None:
    """Main execution function."""
    print("GMR Airports Limited Document Intelligence Extraction")
    print("="*60)
    
    if not validate_configuration():
        print("Error: Invalid configuration")
        return
    
    # Try cloud processing first
    file_names = get_all_blobs_from_container()
    
    if file_names:
        print(f"Found {len(file_names)} PDF files in blob storage")
        processed_files, failed_files = process_blob_files(file_names)
        save_summary_report(processed_files, failed_files, "cloud")
    else:
        print("No files in blob storage. Processing local files...")
        processed_files, failed_files = process_local_files()
        save_summary_report(processed_files, failed_files, "local_files")
    
    print_summary(processed_files, failed_files)
    print("\nExtraction completed. Ready for preprocessing pipeline.")


if __name__ == "__main__":
    main()
