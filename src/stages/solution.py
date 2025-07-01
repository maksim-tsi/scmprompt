# Solution development stage implementation
"""
Solution development stage for maritime logistics case generator.

This module implements the solution development stage of the case generation pipeline,
creating comprehensive responses to the logistics challenges presented in the case,
with references to specific regulations and practical recommendations.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..utils.llm import generate_text

# Configure logging
logger = logging.getLogger(__name__)

def develop_solution(case: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
    """
    Develop a comprehensive solution for the enhanced case.
    
    Args:
        case: Dictionary containing the enhanced case
        model: Optional model name to use for generation
        
    Returns:
        Updated case dictionary with solution added
    """
    # Create prompt for solution development
    datapoints_text = ""
    for i, dp in enumerate(case.get("relevant_datapoints", [])[:10]):  # Limit to top 10
        datapoints_text += f"\nDATAPOINT {i+1}:\n"
        datapoints_text += f"Title: {dp.get('title', 'Untitled')}\n"
        datapoints_text += f"Content: {dp.get('content', 'No content')}\n"
        if "relevant_entity" in dp:
            datapoints_text += f"Entity: {dp.get('relevant_entity', 'Unknown')}\n"
    
    # Get the most complete case text version
    case_text = case.get("enhanced_case", case.get("draft_case", ""))
    
    prompt = f"""
    I'll provide you with a MARITIME LOGISTICS CASE. Your task is to:
    1. Develop a comprehensive solution that addresses all aspects of the case
    2. Reference specific regulations and requirements that apply
    3. Explain the reasoning behind each recommendation
    4. Structure the solution clearly with steps/recommendations
    
    CASE TITLE:
    {case.get("title", "Untitled Case")}
    
    CASE SCENARIO:
    {case_text}
    
    RELEVANT DATAPOINTS:
    {datapoints_text}
    
    Please provide a detailed solution that demonstrates understanding of maritime logistics regulations and requirements.
    Structure your response as follows:
    
    ## Executive Summary
    [Brief overview of the situation and solution]
    
    ## Detailed Solution Steps
    [Step-by-step solution with regulatory references]
    
    ## Recommendations
    [Key recommendations and best practices]
    
    ## Risk Mitigation
    [Potential risks and mitigation strategies]
    """
    
    logger.info(f"Developing solution for case: {case.get('title', 'Untitled')}")
    
    # Time the generation
    start_time = datetime.now()
    solution = generate_text(
        prompt=prompt,
        model=model,
        temperature=0.4  # Lower temperature for more focused solution
    )
    duration = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Generated solution with {len(solution)} characters in {duration:.2f}s")
    
    # Update case with solution and metadata
    case.update({
        "solution": solution,
        "solution_complete": True,
        "solution_metadata": {
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "datapoints_referenced": len(case.get("relevant_datapoints", [])),
            "solution_version": "2.0",
            "generation_duration": duration,
            "prompt_tokens": len(prompt),  # Approximate token count
            "solution_structure": "four_part"  # Track solution structure version
        }
    })
    
    return case

def generate_executive_summary(case: Dict[str, Any], model: Optional[str] = None) -> str:
    """
    Generate a concise executive summary for the case solution.
    
    Args:
        case: Dictionary containing the case with solution
        model: Optional model name to use for generation
        
    Returns:
        Executive summary text
    """
    # Check if we already have a solution
    if "solution" not in case:
        logger.warning("No solution found in case, cannot generate executive summary")
        return "No solution available to summarize."
    
    # Create prompt for summary generation
    prompt = f"""
    I'll provide you with a CASE TITLE and SOLUTION. Your task is to create a concise executive summary.
    
    CASE TITLE:
    {case.get("title", "Untitled Case")}
    
    SOLUTION:
    {case.get("solution", "No solution available")}
    
    Please create a concise executive summary (max 150 words) that:
    1. Summarizes the key issues in the case
    2. Outlines the core recommendations
    3. Highlights the expected outcomes
    
    EXECUTIVE SUMMARY:
    """
    
    logger.info("Generating executive summary")
    
    # Generate summary with low temperature for precision
    summary = generate_text(
        prompt=prompt,
        model=model,
        temperature=0.2,
        max_tokens=300  # Limit to ensure conciseness
    )
    
    # Add to case metadata
    if "solution_metadata" not in case:
        case["solution_metadata"] = {}
    
    case["solution_metadata"]["executive_summary"] = summary
    
    return summary

def evaluate_solution_quality(case: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluate the quality of the generated solution.
    
    Args:
        case: Dictionary containing the case with solution
        model: Optional model name to use for evaluation
        
    Returns:
        Dictionary with evaluation metrics
    """
    # Create prompt for evaluation
    prompt = f"""
    I'll provide you with a CASE and its SOLUTION. Your task is to evaluate the quality of the solution.
    
    CASE:
    {case.get("enhanced_case", case.get("draft_case", "No case available"))}
    
    SOLUTION:
    {case.get("solution", "No solution available")}
    
    Please evaluate the solution on the following criteria (score 1-10 and justify):
    
    1. Regulatory Accuracy: Does it correctly reference relevant regulations?
    2. Comprehensiveness: Does it address all key issues in the case?
    3. Practicality: Are the recommendations realistic and implementable?
    4. Structure and Clarity: Is the solution well-organized and clear?
    5. Risk Assessment: Does it identify and mitigate potential risks?
    
    For each criterion, provide:
    - Score (1-10)
    - Brief justification
    - Suggestion for improvement
    
    Then provide an overall quality score (1-10) with summary assessment.
    """
    
    logger.info("Evaluating solution quality")
    
    # Generate evaluation with low temperature for consistency
    evaluation = generate_text(
        prompt=prompt,
        model=model,
        temperature=0.2
    )
    
    # Process evaluation to extract overall score (simple heuristic)
    import re
    
    # Try to extract overall score using regex
    overall_score = 0
    score_match = re.search(r"overall quality score:?\s*(\d+)", evaluation, re.IGNORECASE)
    if score_match:
        try:
            overall_score = int(score_match.group(1))
        except ValueError:
            overall_score = 0
    
    # Create evaluation results
    evaluation_results = {
        "evaluation_text": evaluation,
        "overall_score": overall_score,
        "evaluation_timestamp": datetime.now().isoformat(),
        "evaluation_model": model
    }
    
    # Add to case metadata
    if "solution_metadata" not in case:
        case["solution_metadata"] = {}
    
    case["solution_metadata"]["quality_evaluation"] = evaluation_results
    
    return evaluation_results

def generate_teaching_notes(case: Dict[str, Any], model: Optional[str] = None) -> str:
    """
    Generate teaching notes for using the case in an educational setting.
    
    Args:
        case: Dictionary containing the case with solution
        model: Optional model name to use for generation
        
    Returns:
        Teaching notes text
    """
    # Create prompt for teaching notes
    prompt = f"""
    I'll provide you with a CASE STUDY and its SOLUTION. Your task is to create teaching notes for instructors.
    
    CASE TITLE:
    {case.get("title", "Untitled Case")}
    
    CASE:
    {case.get("enhanced_case", case.get("draft_case", ""))[:1500]}...
    
    SOLUTION (Key points):
    {case.get("solution", "No solution available")[:1500]}...
    
    Please create comprehensive teaching notes that include:
    
    ## Learning Objectives
    [List 3-5 specific learning objectives this case addresses]
    
    ## Key Discussion Points
    [Outline 4-6 key points for classroom discussion]
    
    ## Teaching Approach
    [Suggest how to present and facilitate discussion of this case]
    
    ## Assessment Questions
    [Provide 3-5 questions to assess student understanding]
    
    ## Additional Resources
    [Suggest relevant regulations, articles or other materials]
    """
    
    logger.info("Generating teaching notes")
    
    # Generate notes with medium temperature for educational content
    teaching_notes = generate_text(
        prompt=prompt,
        model=model,
        temperature=0.5
    )
    
    # Add to case metadata
    case["teaching_notes"] = teaching_notes
    
    return teaching_notes