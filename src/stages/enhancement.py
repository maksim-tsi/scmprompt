"""
Enhancement stage for maritime logistics case generator.

This module implements the contextual enhancement stage of the case generation pipeline,
adding specific regulatory details, domain knowledge, and realistic logistics 
processes based on retrieved datapoints and domain-specific guidelines.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..utils.llm import generate_text
from ..utils.vector_db import get_qdrant_client, create_embeddings

# Configure logging
logger = logging.getLogger(__name__)

def find_relevant_guideline(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find the most relevant domain-specific guideline for a case.
    
    Args:
        case: Dictionary containing the case with draft text
        
    Returns:
        Dictionary with guideline content and metadata
    """
    from qdrant_client.http import models
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    # Get the client and collection name
    client = get_qdrant_client()
    references_collection = os.getenv("REFERENCES_COLLECTION", "case_generation_references")
    
    try:
        # Create a query from the case draft
        query_text = case.get("draft_case", "")[:5000]  # Limit length for API
        query_embedding = create_embeddings(query_text)
        
        if not query_embedding:
            logger.error("Failed to create embedding for case draft")
            return {}
        
        # Search for domain-specific guidelines
        results = client.search(
            collection_name=references_collection,
            query_vector=query_embedding,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="content_type", 
                        match=models.MatchValue(value="guideline")
                    ),
                ],
                must_not=[
                    models.FieldCondition(
                        key="guideline_type",
                        match=models.MatchValue(value="general")
                    )
                ]
            ),
            limit=5,
            with_payload=True,
            with_vectors=False  # Optimize by not retrieving vectors
        )
        
        if not results:
            logger.warning("No relevant guidelines found")
            return {}
        
        # Get the top guideline
        top_guideline = results[0].payload
        guideline_type = top_guideline.get("guideline_type", "unknown")
        logger.info(f"Found relevant guideline: {guideline_type} (score: {results[0].score:.4f})")
        
        # Add all relevant guideline chunks
        guideline_content = ""
        for result in results:
            if "content" in result.payload:
                guideline_content += result.payload["content"] + "\n\n"
        
        return {
            "guideline_type": guideline_type,
            "content": guideline_content,
            "score": results[0].score,
            "title": top_guideline.get('title', 'Untitled Guideline'),
            "chunks_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error finding relevant guideline: {str(e)}")
        return {}

def get_default_guideline() -> str:
    """
    Get the default maritime logistics guideline.
    
    Returns:
        String containing default guideline text
    """
    return """
    Maritime logistics cases should demonstrate realistic challenges in container shipping,
    including proper documentation, customs procedures, and regulatory compliance.
    Focus on real-world scenarios between Asia and Northern Europe/Baltic regions.
    Include accurate references to:
    - Port operations and procedures
    - Documentation requirements (bill of lading, certificates, etc.)
    - Customs clearance processes
    - International shipping regulations
    - Container handling best practices
    """

def enhance_case_with_context(case: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
    """
    Enhance the case with datapoints and domain-specific guidelines.
    
    Args:
        case: Dictionary containing the case with draft text and analysis
        model: Optional model name to use for generation
        
    Returns:
        Updated case dictionary with enhanced content
    """
    # Find relevant guideline
    guideline = find_relevant_guideline(case)
    
    if not guideline or not guideline.get("content"):
        logger.warning("No relevant guideline found, using default")
        guideline = {
            "guideline_type": "default_maritime",
            "content": get_default_guideline(),
            "chunks_found": 0
        }
    else:
        logger.info(f"Found guideline: {guideline.get('guideline_type')} "
                   f"with {guideline.get('chunks_found')} chunks")
    
    # Prepare datapoints for prompt
    datapoints_text = ""
    for i, dp in enumerate(case.get("relevant_datapoints", [])[:15]):  # Limit to top 15
        datapoints_text += f"\nDATAPOINT {i+1}:\n"
        datapoints_text += f"Title: {dp.get('title', 'Untitled')}\n"
        datapoints_text += f"Content: {dp.get('content', 'No content')}\n"
        if "port_area" in dp:
            datapoints_text += f"Port Area: {dp.get('port_area', 'Unknown')}\n"
        if "relevant_entity" in dp:
            datapoints_text += f"Entity: {dp.get('relevant_entity', 'Unknown')}\n"
    
    # Create prompt for enhancement
    prompt = f"""
    I'll provide you with a DRAFT CASE, DATAPOINTS, and DOMAIN GUIDELINES. Your task is to:
    1. Enhance the case with specific regulatory details from the datapoints
    2. Ensure it follows domain-specific guidelines 
    3. Make the scenario more realistic and educational
    4. Add a clear title for the case
    
    DRAFT CASE:
    {case.get("draft_case", "")}
    
    RELEVANT DATAPOINTS:
    {datapoints_text}
    
    DOMAIN GUIDELINES:
    {guideline.get("content", "")}
    
    Please respond with:
    
    ## Case Title
    [Provide a concise, descriptive title for this case]
    
    ## Enhanced Case
    [Provide the improved case with specific regulations and requirements from the datapoints]
    """
    
    logger.info(f"Enhancing case with contextual information...")
    
    # Time the LLM call
    start_time = datetime.now()
    enhanced_content = generate_text(
        prompt=prompt,
        model=model,
        temperature=0.7  # Higher temperature for creative enhancement
    )
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Generated enhanced case in {duration:.2f}s")
    
    # Extract title and enhanced case
    title = "Untitled Case"
    enhanced_case = enhanced_content
    
    if "## Case Title" in enhanced_content:
        parts = enhanced_content.split("## Case Title")
        title_section = parts[1].split("##")[0]
        title = title_section.strip()
        
    if "## Enhanced Case" in enhanced_content:
        parts = enhanced_content.split("## Enhanced Case")
        enhanced_case = parts[1].strip()
    
    # Update case with enhanced metadata
    case.update({
        "title": title,
        "enhanced_case": enhanced_case,
        "domain_guideline": guideline.get("guideline_type", "default"),
        "enhancement_metadata": {
            "model": model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "datapoints_used": len(case.get("relevant_datapoints", [])),
            "guideline_type": guideline.get("guideline_type", "default"),
            "guideline_chunks": guideline.get("chunks_found", 0),
            "enhancement_duration": duration
        }
    })
    
    return case

def merge_datapoint_references(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple datapoints into cohesive reference blocks by topic.
    
    This function organizes datapoints by topic before enhancement,
    improving context integration in the enhanced case.
    
    Args:
        case: Dictionary containing the case with relevant datapoints
        
    Returns:
        Updated case with organized reference blocks
    """
    datapoints = case.get("relevant_datapoints", [])
    if not datapoints:
        return case
    
    # Group datapoints by topic/entity
    topic_groups = {}
    
    for dp in datapoints:
        # Determine the topic key (use entity, type, or both)
        entity = dp.get("relevant_entity", "").lower()
        dp_type = dp.get("datapoint_type", "").lower()
        
        if entity and dp_type:
            key = f"{entity}_{dp_type}"
        elif entity:
            key = entity
        elif dp_type:
            key = dp_type
        else:
            key = "misc"
        
        # Add to appropriate group
        if key not in topic_groups:
            topic_groups[key] = []
        topic_groups[key].append(dp)
    
    # Create reference blocks
    reference_blocks = []
    
    for topic, points in topic_groups.items():
        if len(points) == 1:
            # Single datapoint, use as is
            reference_blocks.append(points[0])
        else:
            # Merge multiple datapoints
            merged_content = f"## {topic.replace('_', ' ').title()} Information\n\n"
            
            for i, point in enumerate(points, 1):
                merged_content += f"- {point.get('title', 'Information')}:\n"
                merged_content += f"  {point.get('content', '')}\n\n"
            
            # Create merged datapoint
            merged_dp = {
                "id": f"merged_{topic}",
                "title": f"{topic.replace('_', ' ').title()} Combined Information",
                "content": merged_content,
                "datapoint_type": "merged",
                "relevant_entity": topic.split('_')[0] if '_' in topic else "",
                "search_score": max(p.get("search_score", 0) for p in points),
                "merged_count": len(points),
                "merged_ids": [p.get("id", "") for p in points]
            }
            
            reference_blocks.append(merged_dp)
    
    # Add reference blocks to case
    case["reference_blocks"] = reference_blocks
    
    return case

def enhance_case_with_style_guidance(
    case: Dict[str, Any], 
    style: str = "educational", 
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enhance the case with specific style guidance.
    
    Args:
        case: Dictionary containing the case with draft text
        style: Style guidance to apply (educational, narrative, technical)
        model: Optional model name to use for generation
        
    Returns:
        Updated case dictionary with enhanced content
    """
    # Get the base case text (draft or enhanced)
    case_text = case.get("enhanced_case", case.get("draft_case", ""))
    
    # Define style guidance prompts
    style_guidance = {
        "educational": """
            Enhance the case to be more educational by:
            - Including more specific references to regulations and requirements
            - Explaining key concepts within the narrative
            - Adding clear learning objectives through the problems presented
            - Maintaining academic tone while still being engaging
        """,
        "narrative": """
            Enhance the case with better narrative elements by:
            - Adding more character development for key stakeholders
            - Creating a clearer story arc with setup, complication, and resolution points
            - Using more vivid descriptions of settings and situations
            - Including realistic dialogue where appropriate
        """,
        "technical": """
            Enhance the case with more technical detail by:
            - Including specific technical specifications relevant to the scenario
            - Adding more precise logistical and operational details
            - Incorporating industry-standard terminology and processes
            - Focusing on technical problems and solutions
        """
    }
    
    # Get appropriate guidance
    guidance = style_guidance.get(style, style_guidance["educational"])
    
    # Create prompt for enhancement
    prompt = f"""
    I'll provide you with a CASE that needs to be enhanced with a specific STYLE GUIDANCE.

    CASE:
    {case_text}

    STYLE GUIDANCE:
    {guidance}
    
    Please enhance the case following the style guidance, while preserving the core scenario and educational value.
    Maintain the same overall structure and key elements, but improve the case according to the guidance.
    
    ENHANCED CASE:
    """
    
    logger.info(f"Enhancing case with {style} style guidance...")
    
    # Generate enhanced case
    enhanced_case = generate_text(
        prompt=prompt,
        model=model,
        temperature=0.6
    )
    
    # Update case with style enhancement
    case["style_enhanced_case"] = enhanced_case
    case["style_guidance"] = style
    
    return case# Contextual enhancement stage implementation
