"""
Maritime Logistics Case Generation Pipeline Runner

This module provides the core pipeline orchestration for the maritime case generation system,
coordinating the flow between various stages and managing checkpoints/logging.
"""

import os
import time
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

# Import project configuration
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))  # Add project root to path
import config  # This will execute the configuration code and configure Google API

# Import stage-specific modules
from ..stages.draft_generation import select_random_example, generate_case_draft
from ..stages.analysis import analyze_case_draft, extract_queries_and_keywords
from ..stages.datapoint_retrieval import retrieve_relevant_datapoints
from ..stages.enhancement import find_relevant_guideline, enhance_case_with_context
from ..stages.solution import develop_solution, generate_teaching_notes

# Import utilities
from ..models.logger import CaseGenerationLogger
from ..pipeline.checkpointing import initialize_checkpoint, save_checkpoint, load_checkpoint

# Configure logging
logger = logging.getLogger(__name__)

def log_stage_error(case: Dict[str, Any], stage_name: str, error: Exception) -> str:
    """
    Log an error that occurred during a pipeline stage.
    
    Args:
        case: The case dictionary
        stage_name: Name of the stage where error occurred
        error: The exception that was raised
        
    Returns:
        Error message string
    """
    error_msg = str(error)
    print(f"\n❌ ERROR IN {stage_name.upper()}: {error_msg}")
    
    if 'logger' in case:
        case['logger'].error(f"{stage_name.upper()}_ERROR", f"Error in {stage_name}: {error_msg}", {
            "error": error_msg,
            "stage": stage_name
        })
        case['logger'].end_stage(success=False, result_summary={"error": error_msg})
    
    print("\nStack trace:")
    traceback.print_exc()
    
    return error_msg

def save_final_case(case: Dict[str, Any]) -> Path:
    """
    Save the final case to output directory.
    
    Args:
        case: The completed case dictionary
        
    Returns:
        Path to the saved file
    """
    from ..pipeline.checkpointing import make_json_serializable
    import json
    
    # Create a sanitized file name for the case
    title = case.get("title", "Untitled_Case")
    sanitized_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title).replace(" ", "_")
    
    # Get the case ID
    case_id = case.get("case_id", "unknown")
    
    # Create the output directory if it doesn't exist
    output_dir = Path(__file__).parents[2] / "Output" / "Generated_Cases"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare the case copy for saving (remove logger and make serializable)
    case_copy = make_json_serializable(case)
    if "logger" in case_copy:
        del case_copy["logger"]
    
    # Save the file
    filepath = output_dir / f"{sanitized_title}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(case_copy, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Final case saved to {filepath}")
    
    return filepath

def run_case_generation_pipeline(
    resume_from: Optional[str] = None, 
    save_checkpoints: bool = True,
    debug: bool = True,
    generate_teaching_materials: bool = False,
    llm_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run the full maritime case generation pipeline with checkpoint saving and logging.
    
    The pipeline consists of 5 main stages:
    1. Draft Generation - Create initial case draft based on an example
    2. Analysis - Analyze the draft and generate search queries
    3. Datapoint Retrieval - Find relevant regulations and guidelines
    4. Enhancement - Improve the case with specific details
    5. Solution Development - Create a comprehensive solution
    
    Args:
        resume_from: Optional case ID to resume from a checkpoint
        save_checkpoints: Whether to save checkpoints after each stage
        debug: Whether to print additional debug information
        generate_teaching_materials: Whether to generate teaching notes (optional)
        llm_model: Optional override for the LLM model name
        
    Returns:
        The completed case dictionary
    """
    case = None
    
    # Debug mode indication
    if debug:
        print("🔍 Running pipeline in DEBUG mode")
    
    # Get model from environment/config if not specified
    if not llm_model:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        llm_model = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
        if debug:
            print(f"Using LLM model: {llm_model}")
    
    # Resume from existing checkpoint if requested
    if resume_from:
        case = load_checkpoint(resume_from)
        if not case:
            print(f"Could not load checkpoint {resume_from}, starting new case")
    
    # Initialize new case if not resuming
    if not case:
        print("STAGE 0: INITIALIZATION")
        case = initialize_checkpoint()
        print(f"Created new case with ID: {case['case_id']}")
    
    # Initialize logger
    case_logger = CaseGenerationLogger(case_id=case['case_id'])
    case['logger'] = case_logger  # Store reference to logger
    
    # Track the current stage
    current_stage = case.get("last_checkpoint", "initialized")
    
    try:
        # Stage 1: Case Draft Generation
        if current_stage in ["initialized"]:
            case_logger.start_stage("draft_generation")
            print(f"\nSTAGE 1: CASE DRAFT GENERATION (using {llm_model})")
            
            try:
                if debug: print("  1.1 Selecting random example case...")
                example_case = select_random_example()
                case_logger.info("EXAMPLE_SELECTED", f"Selected example case", {
                    "example_title": example_case.get('title', 'Unknown'),
                    "example_length": len(str(example_case)) if example_case else 0
                })
                
                if debug: print("  1.2 Generating case draft...")
                # Log LLM request
                summary = example_case.get("summary", "")
                prompt_length = 500  # Base size
                if isinstance(summary, str):
                    prompt_length += min(len(summary), 2000)
                case_logger.log_llm_request(llm_model, prompt_length)
                
                # Time the LLM call
                start_time = datetime.now()
                draft_result = generate_case_draft(example_case, model=llm_model)
                duration = (datetime.now() - start_time).total_seconds()
                
                case.update(draft_result)
                
                # Log LLM response
                case_logger.log_llm_response(
                    llm_model, 
                    len(case.get("draft_case", "")),
                    duration
                )
                
                if debug:
                    print("\nInitial Case Draft Preview:")
                    print("-" * 40)
                    print(case["draft_case"][:500] + "...")
                    print("-" * 40)
                
                case_logger.info("DRAFT_GENERATED", "Case draft generated", {
                    "draft_length": len(case.get("draft_case", "")),
                    "model": llm_model,
                    "generation_duration": duration
                })
                
                case["draft_complete"] = True
                
                if save_checkpoints:
                    if debug: print("  1.3 Saving checkpoint...")
                    save_checkpoint(case, "draft")
                    
                case_logger.end_stage(result_summary={
                    "draft_length": len(case.get("draft_case", "")),
                    "model": llm_model
                })
            except Exception as e:
                log_stage_error(case, "draft_generation", e)
                if not debug:  # If not in debug mode, re-raise to exit
                    raise
        
        # Stage 2: Critical Analysis & Query Generation
        if current_stage in ["initialized", "draft"] and case.get("draft_complete", False):
            case_logger.start_stage("analysis")
            print(f"\nSTAGE 2: CRITICAL ANALYSIS & QUERY GENERATION (using {llm_model})")
            
            try:
                if debug: print("  2.1 Analyzing case draft...")
                # Log LLM request details 
                prompt_length = len(case.get("draft_case", "")) + 1000  # Approximate
                case_logger.log_llm_request(llm_model, prompt_length)
                
                # Time the LLM call
                start_time = datetime.now()
                case = analyze_case_draft(case, model=llm_model)
                duration = (datetime.now() - start_time).total_seconds()
                
                # Log LLM response
                case_logger.log_llm_response(
                    llm_model, 
                    len(case.get("analysis", "")),
                    duration
                )
                
                if debug:
                    print("\nAnalysis Preview:")
                    print("-" * 40)
                    print(case["analysis"][:500] + "...")
                    print("-" * 40)
                
                if debug: print("  2.2 Extracting queries and keywords...")
                # Extract and log queries/keywords
                queries, keywords = extract_queries_and_keywords(case)
                case_logger.info("ANALYSIS_COMPLETE", "Case analysis complete", {
                    "analysis_length": len(case.get("analysis", "")),
                    "query_count": len(queries),
                    "keyword_count": len(keywords),
                    "model": llm_model
                })
                
                case["analysis_complete"] = True
                
                if save_checkpoints:
                    if debug: print("  2.3 Saving checkpoint...")
                    save_checkpoint(case, "analyzed")
                    
                case_logger.end_stage(result_summary={
                    "query_count": len(queries),
                    "keyword_count": len(keywords),
                    "model": llm_model
                })
            except Exception as e:
                log_stage_error(case, "analysis", e)
                if not debug:  # If not in debug mode, re-raise to exit
                    raise
        
        # Stage 3: Retrieve Relevant Datapoints
        if current_stage in ["initialized", "draft", "analyzed"] and case.get("analysis_complete", False):
            case_logger.start_stage("datapoint_retrieval")
            print("\nSTAGE 3: RETRIEVE RELEVANT DATAPOINTS")
            
            try:
                if debug: print("  3.1 Retrieving datapoints...")
                # Time datapoint retrieval
                start_time = datetime.now()
                case = retrieve_relevant_datapoints(case)
                duration = (datetime.now() - start_time).total_seconds()
                
                datapoint_count = len(case.get("relevant_datapoints", []))
                print(f"Retrieved {datapoint_count} datapoints")
                
                case_logger.info("DATAPOINTS_RETRIEVED", f"Retrieved {datapoint_count} datapoints", {
                    "datapoint_count": datapoint_count,
                    "retrieval_duration": duration,
                    "embedding_model": case.get("search_metadata", {}).get("embedding_model", "unknown")
                })
                
                case["datapoints_complete"] = True
                
                if save_checkpoints:
                    if debug: print("  3.2 Saving checkpoint...")
                    save_checkpoint(case, "datapoints_retrieved")
                    
                case_logger.end_stage(result_summary={
                    "datapoint_count": datapoint_count,
                    "retrieval_duration": duration
                })
            except Exception as e:
                log_stage_error(case, "datapoint_retrieval", e)
                if not debug:  # If not in debug mode, re-raise to exit
                    raise
        
        # Stage 4: Contextual Enhancement
        if current_stage in ["initialized", "draft", "analyzed", "datapoints_retrieved"] and case.get("datapoints_complete", False):
            case_logger.start_stage("enhancement")
            print(f"\nSTAGE 4: CONTEXTUAL ENHANCEMENT (using {llm_model})")
            
            try:
                if debug: print("  4.1 Enhancing case with contextual information...")
                # Log LLM request details
                prompt_length = len(case.get("draft_case", "")) + 2000  # Approximate
                case_logger.log_llm_request(llm_model, prompt_length)
                
                # Time the LLM call
                start_time = datetime.now()
                case = enhance_case_with_context(case)
                duration = (datetime.now() - start_time).total_seconds()
                
                # Log LLM response
                case_logger.log_llm_response(
                    llm_model, 
                    len(case.get("enhanced_case", "")),
                    duration
                )
                
                if debug:
                    print("\nEnhanced Case Preview:")
                    print("-" * 40)
                    print(case["enhanced_case"][:500] + "...")
                    print("-" * 40)
                
                case_logger.info("ENHANCEMENT_COMPLETE", "Case enhancement complete", {
                    "enhanced_length": len(case.get("enhanced_case", "")),
                    "title": case.get("title", "Untitled"),
                    "model": llm_model,
                    "guideline_type": case.get("domain_guideline", "none")
                })
                
                case["enhancement_complete"] = True
                
                if save_checkpoints:
                    if debug: print("  4.2 Saving checkpoint...")
                    save_checkpoint(case, "enhanced")
                    
                case_logger.end_stage(result_summary={
                    "title": case.get("title", "Untitled"),
                    "enhanced_length": len(case.get("enhanced_case", "")),
                    "guideline_type": case.get("domain_guideline", "none")
                })
            except Exception as e:
                log_stage_error(case, "enhancement", e)
                if not debug:  # If not in debug mode, re-raise to exit
                    raise
        
        # Stage 5: Solution Development
        if current_stage in ["initialized", "draft", "analyzed", "datapoints_retrieved", "enhanced"] and case.get("enhancement_complete", False):
            case_logger.start_stage("solution")
            print(f"\nSTAGE 5: SOLUTION DEVELOPMENT (using {llm_model})")
            
            try:
                if debug: print("  5.1 Developing comprehensive solution...")
                # Log LLM request details
                prompt_length = len(case.get("enhanced_case", case.get("draft_case", ""))) + 2000  # Approximate
                case_logger.log_llm_request(llm_model, prompt_length)
                
                # Time the LLM call
                start_time = datetime.now()
                case = develop_solution(case, model=llm_model)
                duration = (datetime.now() - start_time).total_seconds()
                
                # Log LLM response
                case_logger.log_llm_response(
                    llm_model, 
                    len(case.get("solution", "")),
                    duration
                )
                
                if debug:
                    print("\nSolution Preview:")
                    print("-" * 40)
                    print(case["solution"][:500] + "...")
                    print("-" * 40)
                
                case_logger.info("SOLUTION_COMPLETE", "Solution development complete", {
                    "solution_length": len(case.get("solution", "")),
                    "model": llm_model,
                    "solution_duration": duration
                })
                
                case["solution_complete"] = True
                
                if save_checkpoints:
                    if debug: print("  5.2 Saving checkpoint...")
                    save_checkpoint(case, "completed")
                    
                case_logger.end_stage(result_summary={
                    "solution_length": len(case.get("solution", "")),
                    "solution_duration": duration
                })
            except Exception as e:
                log_stage_error(case, "solution", e)
                if not debug:  # If not in debug mode, re-raise to exit
                    raise
                    
        # Optional Stage: Teaching Notes Generation
        if generate_teaching_materials and case.get("solution_complete", False):
            case_logger.start_stage("teaching_notes")
            print("\nOPTIONAL STAGE: TEACHING NOTES GENERATION")
            
            try:
                if debug: print("  Generating teaching notes...")
                # Generate teaching notes
                teaching_notes = generate_teaching_notes(case, model=llm_model)
                case["teaching_notes"] = teaching_notes
                
                case_logger.info("TEACHING_NOTES_GENERATED", "Teaching notes generated", {
                    "notes_length": len(teaching_notes),
                    "model": llm_model
                })
                
                if save_checkpoints:
                    save_checkpoint(case, "teaching_notes")
                    
                if debug:
                    print("\nTeaching Notes Preview:")
                    print("-" * 40)
                    print(teaching_notes[:500] + "...")
                    print("-" * 40)
                    
                case_logger.end_stage(result_summary={
                    "notes_length": len(teaching_notes)
                })
            except Exception as e:
                log_stage_error(case, "teaching_notes", e)
                # Continue even if teaching notes generation fails
        
        # Final save and summary
        if case.get("solution_complete", False):
            print("\nCASE GENERATION COMPLETE")
            print(f"Title: {case.get('title', 'Untitled Case')}")
            
            # Save final case to output directory
            final_path = save_final_case(case)
            case["final_path"] = str(final_path)
            
            # Add to case log
            case_logger.info("GENERATION_COMPLETE", "Case generation complete", {
                "title": case.get("title", "Untitled Case"),
                "final_path": str(final_path)
            })
            
            # Log summary
            log_summary = case_logger.finalize()
            case["log_summary"] = log_summary
            
            print("\nGeneration Summary:")
            print(f"- Case ID: {case['case_id']}")
            print(f"- Title: {case.get('title', 'Untitled Case')}")
            print(f"- Draft length: {len(case.get('draft_case', ''))}")
            print(f"- Enhanced length: {len(case.get('enhanced_case', ''))}")
            print(f"- Solution length: {len(case.get('solution', ''))}")
            print(f"- Datapoints used: {len(case.get('relevant_datapoints', []))}")
            if generate_teaching_materials:
                print(f"- Teaching notes: {len(case.get('teaching_notes', ''))}")
            print(f"- Saved to: {final_path}")
        
        return case
        
    except Exception as e:
        print(f"❌ Pipeline execution failed: {str(e)}")
        traceback.print_exc()
        if "logger" in case:
            case["logger"].critical("PIPELINE_FAILED", f"Pipeline execution failed: {str(e)}", {
                "error": str(e),
                "stage": case.get("last_checkpoint", "unknown")
            })
        return case

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the maritime case generation pipeline")
    parser.add_argument("--resume", help="Resume from a specific case ID", default=None)
    parser.add_argument("--no-checkpoints", help="Disable checkpoint saving", action="store_true")
    parser.add_argument("--no-debug", help="Disable debug output", action="store_true")
    parser.add_argument("--teaching-notes", help="Generate teaching notes", action="store_true")
    parser.add_argument("--model", help="Override the LLM model", default=None)
    args = parser.parse_args()
    
    # Run the pipeline with provided arguments
    run_case_generation_pipeline(
        resume_from=args.resume,
        save_checkpoints=not args.no_checkpoints,
        debug=not args.no_debug,
        generate_teaching_materials=args.teaching_notes,
        llm_model=args.model
    )