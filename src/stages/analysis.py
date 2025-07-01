# Analysis stage implementation
"""
Analysis stage for maritime logistics case generator.

This module implements the analysis stage of the case generation pipeline,
examining the case draft, identifying knowledge gaps, and generating
search queries to find relevant information.
"""

import re
import logging
import random
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from ..utils.llm import generate_text
from ..utils.vector_db import get_qdrant_client

# Configure logging
logger = logging.getLogger(__name__)

def get_general_guideline() -> Dict[str, Any]:
    """
    Retrieve the general case generation guideline from vector database.
    
    Returns:
        Dictionary containing guideline text, model used, and count of chunks found
    """
    from qdrant_client.http import models
    import os
    from dotenv import load_dotenv
    from ..utils.vector_db import create_embeddings
    
    load_dotenv()
    
    try:
        # Get client and collection name
        client = get_qdrant_client()
        references_collection = os.getenv("REFERENCES_COLLECTION", "case_generation_references")
        embedding_model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
        
        # Query for general guidelines
        results = client.search(
            collection_name=references_collection,
            query_vector=create_embeddings("general case study guidelines maritime logistics"),
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="guideline_type",
                        match=models.MatchValue(value="general")
                    )
                ]
            ),
            limit=10,
            with_payload=True,
            with_vectors=False  # No need to return vectors
        )
        
        # Combine all general guideline chunks
        guideline_text = ""
        for result in results:
            if "content" in result.payload:
                guideline_text += result.payload["content"] + "\n\n"
        
        logger.info(f"Retrieved {len(results)} general guideline chunks")
        
        return {
            "text": guideline_text,
            "model": embedding_model,
            "chunks_found": len(results)
        }
    
    except Exception as e:
        logger.error(f"Error retrieving general guidelines: {str(e)}")
        # Return fallback guideline
        return {
            "text": """
            Maritime logistics cases should demonstrate realistic challenges in container shipping,
            including proper documentation, customs procedures, and regulatory compliance.
            Focus on real-world scenarios between Asia and Northern Europe/Baltic regions.
            """,
            "model": "fallback",
            "chunks_found": 0
        }

def analyze_case_draft(case: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze the case draft against guidelines and generate search queries.
    
    Args:
        case: Dictionary containing the case draft and metadata
        model: Optional model name to use for generation
        
    Returns:
        Updated case dictionary with analysis added
    """
    # Get general guidelines
    guideline = get_general_guideline()
    
    # Create prompt for analysis
    prompt = f"""
    I'll provide you with a DRAFT CASE and GUIDELINES for case creation. Your task is to:
    1. Critically analyze the case against the guidelines
    2. Identify topics and concepts that need to be researched in our datapoints
    3. Generate search queries to find relevant regulations and requirements
    
    GUIDELINES:
    {guideline.get('text', '')[:3000]}  # Truncate if too long
    
    DRAFT CASE:
    {case.get("draft_case", "")}
    
    Please respond with:
    
    ## Case Analysis
    [Provide a critical assessment of the draft case against the guidelines]
    
    ## Knowledge Gaps
    [List specific areas where more regulatory/requirement information is needed]
    
    ## Search Queries
    [Provide 10 specific search queries that would help find relevant datapoints in our database]
    
    ## Keywords
    [List 10-15 specific keywords that are most relevant to this case]
    """
    
    logger.info("Analyzing case draft and generating search queries...")
    
    # Time the LLM call
    start_time = datetime.now()
    analysis = generate_text(prompt, model=model, temperature=0.3)
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Generated analysis: {len(analysis)} chars in {duration:.2f}s")
    
    # Add analysis to the case
    case["analysis"] = analysis
    case["analysis_timestamp"] = datetime.now().isoformat()
    case["analysis_duration"] = duration
    case["analysis_model"] = model
    
    return case

def extract_queries_and_keywords(case: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Extract search queries and keywords from the case analysis.
    
    Args:
        case: Dictionary containing case analysis
        
    Returns:
        Tuple of (search queries list, keywords list)
    """
    analysis = case.get("analysis", "")
    
    # Try to extract queries
    queries = []
    if "## Search Queries" in analysis:
        queries_section = analysis.split("## Search Queries")[1].split("##")[0]
        for line in queries_section.strip().split("\n"):
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                # Remove leading numbers or bullet points
                clean_line = re.sub(r"^\d+\.\s*|\-\s*", "", clean_line)
                if clean_line:
                    queries.append(clean_line)
    
    # Try to extract keywords
    keywords = []
    if "## Keywords" in analysis:
        keywords_section = analysis.split("## Keywords")[1].split("##")[0] if "##" in analysis.split("## Keywords")[1] else analysis.split("## Keywords")[1]
        for line in keywords_section.strip().split("\n"):
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                # Remove leading numbers or bullet points
                clean_line = re.sub(r"^\d+\.\s*|\-\s*", "", clean_line)
                if clean_line:
                    for word in clean_line.split(","):
                        word = word.strip()
                        if word:
                            keywords.append(word)
    
    # If no queries or keywords found, generate some default ones
    if not queries:
        logger.warning("No search queries found in analysis, using defaults")
        queries = [
            "maritime logistics requirements", 
            "container shipping documentation", 
            "customs clearance procedures",
            "international shipping regulations",
            "port operations standards"
        ]
    
    if not keywords:
        logger.warning("No keywords found in analysis, using defaults")
        keywords = [
            "logistics", 
            "shipping", 
            "maritime", 
            "container", 
            "customs", 
            "documentation", 
            "regulations",
            "compliance"
        ]
    
    logger.info(f"Extracted {len(queries)} queries and {len(keywords)} keywords")
    
    # Add to case for reference
    case["search_queries"] = queries
    case["keywords"] = keywords
    
    return queries, keywords

def scan_case_for_focus_areas(case_text: str) -> List[str]:
    """
    Scan case text to identify main focus areas.
    
    Args:
        case_text: The case text to analyze
        
    Returns:
        List of identified focus areas
    """
    # Define common focus areas in maritime logistics
    focus_areas = {
        "customs": ["customs", "clearance", "declaration", "duty", "import", "export"],
        "documentation": ["documentation", "bill of lading", "certificate", "manifest", "packing list"],
        "compliance": ["compliance", "regulation", "requirement", "law", "directive"],
        "shipping": ["vessel", "container", "carrier", "shipping", "transit"],
        "port_operations": ["port", "terminal", "loading", "unloading", "berthing"]
    }
    
    # Count occurrences of keywords
    area_scores = {area: 0 for area in focus_areas}
    
    for area, keywords in focus_areas.items():
        for keyword in keywords:
            area_scores[area] += len(re.findall(r'\b' + re.escape(keyword) + r'\b', case_text.lower()))
    
    # Sort areas by score
    sorted_areas = sorted(area_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top areas (those with at least one match)
    return [area for area, score in sorted_areas if score > 0]

def analyze_with_focus(case: Dict[str, Any], focus_area: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze case with specific focus area guidance.
    
    Args:
        case: Dictionary containing the case draft
        focus_area: Specific area to focus analysis on (e.g., "customs", "documentation")
        model: Optional model name to use for generation
        
    Returns:
        Updated case with focused analysis
    """
    # Get general guidelines
    guideline = get_general_guideline()
    
    # Create focused prompt
    prompt = f"""
    I'll provide you with a DRAFT CASE and GUIDELINES. Your task is to analyze it with special focus on {focus_area.upper()}.
    
    DRAFT CASE:
    {case.get("draft_case", "")}
    
    GUIDELINES:
    {guideline.get('text', '')[:2000]}
    
    Please focus your analysis specifically on {focus_area} aspects of the case, including:
    1. Identify specific {focus_area} requirements, processes and challenges in the case
    2. Point out areas where more detailed {focus_area} information would improve the case
    3. Generate search queries specifically focused on finding {focus_area} regulations and requirements
    
    Format your response with these sections:
    
    ## {focus_area.title()} Analysis
    [Detailed analysis of {focus_area} aspects]
    
    ## {focus_area.title()} Knowledge Gaps
    [Specific {focus_area} information needed]
    
    ## {focus_area.title()} Search Queries
    [8-10 search queries focused on {focus_area}]
    
    ## {focus_area.title()} Keywords
    [10-15 keywords specifically relevant to {focus_area} aspects of the case]
    """
    
    logger.info(f"Analyzing case with focus on {focus_area}...")
    
    # Time the LLM call
    start_time = datetime.now()
    focused_analysis = generate_text(prompt, model=model, temperature=0.3)
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Generated focused analysis on {focus_area}: {len(focused_analysis)} chars in {duration:.2f}s")
    
    # Store as a separate field
    case[f"focused_analysis_{focus_area}"] = focused_analysis
    
    # Extract focused queries
    focused_queries = []
    if f"## {focus_area.title()} Search Queries" in focused_analysis:
        queries_section = focused_analysis.split(f"## {focus_area.title()} Search Queries")[1].split("##")[0]
        for line in queries_section.strip().split("\n"):
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                clean_line = re.sub(r"^\d+\.\s*|\-\s*", "", clean_line)
                if clean_line:
                    focused_queries.append(clean_line)
    
    # Add to case metadata
    if not "focused_queries" in case:
        case["focused_queries"] = {}
    case["focused_queries"][focus_area] = focused_queries
    
    return case