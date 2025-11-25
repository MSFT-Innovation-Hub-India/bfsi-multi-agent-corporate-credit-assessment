import traceback
import os
import sys
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.pdf_generator_agent import convert_txt_to_html

def pdf_generator_pipeline():
    """
    Pipeline for GMR PDF Generator Agent
    Returns structured output for semantic kernel integration
    """
    try:
        # Import output configuration
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from config import get_output_paths
        output_paths = get_output_paths()
        
        # Execute PDF generator using direct import
        generator_result = convert_txt_to_html()
        
        # Check generated files dynamically - files will be in frontend directory
        html_file = output_paths["comprehensive_html"]
        pdf_file = html_file.replace('.html', '.pdf')  # Construct PDF path from HTML path
        
        generated_files = []
        file_details = []
        
        if os.path.exists(html_file):
            html_size = os.path.getsize(html_file)
            generated_files.append("✅ HTML")
            file_details.append(f"HTML ({html_size:,} bytes)")
        else:
            generated_files.append("❌ HTML")
        
        if os.path.exists(pdf_file):
            pdf_size = os.path.getsize(pdf_file)
            generated_files.append("✅ PDF")
            file_details.append(f"PDF ({pdf_size:,} bytes)")
        else:
            generated_files.append("❌ PDF")
        
        # Create dynamic response
        files_status = " | ".join(generated_files)
        files_info = " | ".join(file_details) if file_details else "No files generated"
        
        if generator_result:
            response = f"📄 PDF GENERATOR RESULT: Successfully generated report files | 🎯 FILES STATUS: {files_status} | 📊 DETAILS: {files_info}"
        else:
            response = f"📄 PDF GENERATOR FAILED: Failed to generate report files | 🎯 FILES STATUS: {files_status} | 📊 DETAILS: {files_info}"
        
        status = "AgentStatus.complete"
        error = None
        
    except Exception as e:
        response = None
        status = "AgentStatus.failed"
        error = str(e) + "\n" + traceback.format_exc()
        
    return {
        "agentName": "GMR PDF Generator Agent",
        "agentDescription": "Converts credit analysis text file to professional HTML and PDF report.",
        "response": response,
        "completedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "errorMessage": error
    }

if __name__ == "__main__":
    import json
    print(json.dumps(pdf_generator_pipeline(), indent=2))
