"""
Template Loader Utility for GMR Semantic Kernel Orchestration
Loads prompts and instructions from JSON and TXT files in Templates directory
"""

import json
import os
from pathlib import Path

class TemplateLoader:
    """Utility class to load agent prompts and instructions from template files"""
    
    def __init__(self):
        """Initialize template loader with base path"""
        # Templates folder is in the parent directory (Semantic_kernel_Orchestration/Templates/)
        self.base_path = Path(__file__).parent.parent / "Templates"
        self.prompts_path = self.base_path / "prompts"
        self.instructions_path = self.base_path / "instructions"
    
    def load_prompts(self, filename):
        """
        Load prompts from JSON file
        
        Args:
            filename: Name of JSON file in Templates/prompts/ directory
            
        Returns:
            dict: Dictionary containing section prompts
        """
        filepath = self.prompts_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Prompts file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_instruction(self, filename):
        """
        Load agent instruction from TXT file
        
        Args:
            filename: Name of TXT file in Templates/instructions/ directory
            
        Returns:
            str: Agent instruction text
        """
        filepath = self.instructions_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Instruction file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def get_proposal_verification_sections(self):
        """Load proposal verification section prompts"""
        return self.load_prompts("proposal_verification_sections.json")
    
    def get_company_profile_sections(self):
        """Load company profile section prompts"""
        return self.load_prompts("company_profile_sections.json")
    
    def get_financial_analysis_sections(self):
        """Load financial analysis section prompts"""
        return self.load_prompts("financial_analysis_sections.json")
    
    def get_proposal_verification_instruction(self):
        """Load proposal verification agent instruction"""
        return self.load_instruction("proposal_verification_agent.txt")
    
    def get_company_profile_instruction(self):
        """Load company profile agent instruction"""
        return self.load_instruction("company_profile_agent.txt")
    
    def get_financial_analysis_instruction(self):
        """Load financial analysis agent instruction"""
        return self.load_instruction("financial_analysis_agent.txt")
    
    def get_market_analyst_instruction(self):
        """Load market analyst agent instruction"""
        return self.load_instruction("market_analyst_agent.txt")
    
    def get_market_analyst_message(self):
        """Load market analyst user message prompt"""
        return self.load_instruction("../prompts/market_analyst_message.txt")
    
    def get_coordinator_instruction(self):
        """Load coordinator agent instruction"""
        return self.load_instruction("coordinator_agent.txt")
    
    def get_annexures_sections(self):
        """Load ANNEXURES section prompts"""
        return self.load_prompts("annexures_sections.json")
    
    def get_verification_analysis_prompt(self):
        """Load verification analysis prompt"""
        filepath = self.prompts_path / "verification_analysis.txt"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Verification analysis prompt file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def get_pdf_generator_instruction(self):
        """Load PDF generator agent instruction"""
        filepath = self.instructions_path / "pdf_generator_agent.txt"
        
        if not filepath.exists():
            raise FileNotFoundError(f"PDF generator instruction file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()


# Convenience functions for backward compatibility
def get_proposal_verification_sections():
    """Get proposal verification section prompts"""
    loader = TemplateLoader()
    return loader.get_proposal_verification_sections()


def get_company_profile_sections():
    """Get company profile section prompts"""
    loader = TemplateLoader()
    return loader.get_company_profile_sections()


def get_financial_analysis_sections():
    """Get financial analysis section prompts"""
    loader = TemplateLoader()
    return loader.get_financial_analysis_sections()


def get_proposal_verification_instruction():
    """Get proposal verification agent instruction"""
    loader = TemplateLoader()
    return loader.get_proposal_verification_instruction()


def get_company_profile_instruction():
    """Get company profile agent instruction"""
    loader = TemplateLoader()
    return loader.get_company_profile_instruction()


def get_financial_analysis_instruction():
    """Get financial analysis agent instruction"""
    loader = TemplateLoader()
    return loader.get_financial_analysis_instruction()


def get_market_analyst_instruction():
    """Get market analyst agent instruction"""
    loader = TemplateLoader()
    return loader.get_market_analyst_instruction()


def get_market_analyst_message():
    """Get market analyst user message prompt"""
    loader = TemplateLoader()
    return loader.get_market_analyst_message()


def get_coordinator_instruction():
    """Get coordinator agent instruction"""
    loader = TemplateLoader()
    return loader.get_coordinator_instruction()


def get_annexures_sections():
    """Get ANNEXURES section prompts"""
    loader = TemplateLoader()
    return loader.get_annexures_sections()


def get_verification_analysis_prompt():
    """Get verification analysis prompt"""
    loader = TemplateLoader()
    return loader.get_verification_analysis_prompt()


def get_pdf_generator_instruction():
    """Get PDF generator agent instruction"""
    loader = TemplateLoader()
    return loader.get_pdf_generator_instruction()


if __name__ == "__main__":
    # Test the template loader
    loader = TemplateLoader()
    
    print("Testing Template Loader...")
    print("\n1. Loading Proposal Verification Sections:")
    pv_sections = loader.get_proposal_verification_sections()
    print(f"   Loaded {len(pv_sections)} sections")
    
    print("\n2. Loading Company Profile Sections:")
    cp_sections = loader.get_company_profile_sections()
    print(f"   Loaded {len(cp_sections)} sections")
    
    print("\n3. Loading Financial Analysis Sections:")
    fa_sections = loader.get_financial_analysis_sections()
    print(f"   Loaded {len(fa_sections)} sections")
    
    print("\n4. Loading Instructions:")
    pv_instruction = loader.get_proposal_verification_instruction()
    print(f"   Proposal Verification: {len(pv_instruction)} characters")
    
    cp_instruction = loader.get_company_profile_instruction()
    print(f"   Company Profile: {len(cp_instruction)} characters")
    
    fa_instruction = loader.get_financial_analysis_instruction()
    print(f"   Financial Analysis: {len(fa_instruction)} characters")
    
    print("\n✅ All templates loaded successfully!")
