"""
Draft generation stage for maritime logistics case generator.

This module implements the first stage of the case generation pipeline,
selecting example cases and generating initial case drafts.
"""

import time
import random
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from ..utils.llm import generate_text
from ..utils.vector_db import get_qdrant_client

# Configure logging
logger = logging.getLogger(__name__)

def select_random_example() -> Dict[str, Any]:
    """
    Select a random example case from the reference database.
    
    Returns:
        Dictionary containing the example case details
    """
    from qdrant_client.http import models
    
    try:
        # Get client from config
        client = get_qdrant_client()
        
        # Get collection name from config
        from dotenv import load_dotenv
        import os
        load_dotenv()
        references_collection = os.getenv("REFERENCES_COLLECTION", "case_generation_references")
        
        # Get all examples
        examples, _ = client.scroll(
            collection_name=references_collection,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="content_type",
                        match=models.MatchValue(value="example")
                    )
                ]
            ),
            limit=100,
            with_payload=True
        )
        
        if not examples:
            logger.warning("No example cases found in the database")
            # Return a default example
            return {
                "title": "Default Example",
                "summary": "This is a default example case for maritime logistics training. It involves a vessel carrying containers between ports, with delays and regulatory issues.",
                "filename": "default_example.md"
            }
        
        # Select a random example
        example = random.choice(examples)
        logger.info(f"Selected example: {example.payload.get('title', 'Untitled')}")
        
        return example.payload
        
    except Exception as e:
        logger.error(f"Error retrieving examples: {str(e)}")
        # Return a default example as fallback
        return {
            "title": "Default Example",
            "summary": "This is a default example case for maritime logistics training. It involves a vessel carrying containers between ports, with delays and regulatory issues.",
            "filename": "default_example.md"
        }

def generate_case_draft(example_case: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate initial case draft based on an example case.
    
    Args:
        example_case: Dictionary containing the example case to use as inspiration
        model: Optional model name to use for generation
    
    Returns:
        Dictionary containing the draft case and metadata
    """
    # Create prompt for case generation
    prompt = f"""
    You are tasked with creating a new case study for maritime logistics training.
    
    I'll provide you with an EXAMPLE CASE for inspiration. Your task is to create a NEW CASE that:
    1. Is in a similar domain but with entirely different details
    2. Focuses on container shipping logistics between Asia and Northern Europe/Baltic
    3. Involves realistic operational challenges
    4. References specific ports, companies, and vessels (use realistic but fictional names)
    5. Presents a clear problem that needs resolution
    
    DO NOT copy the example directly - create something new that tests similar knowledge.
    
    EXAMPLE CASE SUMMARY:
    {example_case.get('summary', 'No summary available')}
    
    NEW CASE (write only the case description, not the solution):
    """
    
    logger.info("Generating initial case draft...")
    
    # Time the LLM call
    start_time = datetime.now()
    case_draft = generate_text(
        prompt=prompt,
        model=model,
        temperature=0.7  # Using higher temperature for creativity
    )
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Generated case draft: {len(case_draft)} chars in {duration:.2f}s")
    
    return {
        "example_inspiration": example_case.get('title', 'Unknown example'),
        "example_filename": example_case.get('filename', 'unknown.md'),
        "draft_case": case_draft,
        "creation_date": time.strftime("%Y-%m-%d"),
        "stage": "draft",
        "model": model,  # Store the model used for reference
        "generation_duration": duration
    }

def generate_case_title(case_text: str, model: Optional[str] = None) -> str:
    """
    Generate a title for the case based on its content.
    
    Args:
        case_text: The case text to generate a title for
        model: Optional model name to use for generation
        
    Returns:
        The generated title
    """
    # Create prompt for title generation
    prompt = f"""
    Based on the following case study, create a concise, professional title that:
    1. Captures the core challenge or situation
    2. Mentions the key company or organization
    3. Is under 10 words in length
    
    CASE:
    {case_text[:1000]}
    
    TITLE:
    """
    
    # Generate title with very low temperature for precision
    title = generate_text(prompt, model=model, temperature=0.1)
    
    # Clean up the title (remove quotes or extra formatting)
    title = title.strip().strip('"').strip("'")
    
    return title

def generate_case_with_focus(
    example_case: Dict[str, Any], 
    focus_area: str, 
    region: str,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a case draft with specific focus area and region.
    
    Args:
        example_case: Dictionary containing example case data
        focus_area: Specific logistics area to focus on
        region: Geographical region/route to focus on
        model: Optional model name to use
        
    Returns:
        Dictionary containing the generated case and metadata
    """
    example_summary = example_case.get('summary', '')
    
    prompt = f"""
    Create a new maritime logistics case study scenario inspired by but not copying the example below.
    
    The case should focus specifically on: {focus_area}
    The region/route context should be: {region}
    
    EXAMPLE CASE FOR INSPIRATION:
    {example_summary[:2000]}
    
    IMPORTANT GUIDELINES:
    1. Create a realistic container shipping/logistics scenario with clear problems to solve
    2. Include fictional but plausible company names and stakeholders
    3. Focus on international regulatory compliance and documentation issues
    4. Present specific logistics challenges that require expertise to resolve
    5. The scenario should prompt the reader to consider relevant regulations
    6. Make the case educational while remaining engaging
    7. Include enough specific details to make the case realistic
    8. Focus on the {focus_area} aspects of maritime logistics
    9. Set the scenario in the {region} context
    
    CASE:
    """
    
    logger.info(f"Generating case draft with focus on {focus_area} in {region}...")
    
    # Time the LLM call
    start_time = datetime.now()
    draft_case = generate_text(prompt, model=model, temperature=0.7)
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Generated focused case draft: {len(draft_case)} chars in {duration:.2f}s")
    
    return {
        "draft_case": draft_case,
        "example_inspiration": example_case.get('title', 'Unknown'),
        "focus_area": focus_area,
        "region": region,
        "creation_date": time.strftime("%Y-%m-%d"),
        "stage": "draft",
        "model": model,
        "generation_duration": duration
    }