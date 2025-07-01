"""
Checkpoint management utilities for the Maritime Case Generator pipeline.

This module provides functionality to save, load, and manage checkpoints
during the case generation process, allowing resumption of interrupted runs.
"""

import os
import json
import time
import uuid
import random
import string
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

# Configure base paths
def get_checkpoint_dir() -> Path:
    """Get the directory for storing checkpoints, creating it if needed."""
    checkpoint_dir = Path(__file__).parents[2] / "Data" / "Checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    return checkpoint_dir

def make_json_serializable(obj: Any) -> Any:
    """
    Recursively convert objects to be JSON serializable.
    
    This function handles:
    - Dictionaries (recursively processed)
    - Lists and tuples (recursively processed)
    - Custom objects with __dict__ attributes
    - Removes logger objects and callable items
    - Returns primitive types directly
    
    Args:
        obj: Object to make JSON serializable
        
    Returns:
        JSON serializable version of the object
    """
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items() 
                if k != "logger" and not callable(v)}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(i) for i in obj]
    elif hasattr(obj, '__dict__'):
        # Convert custom objects to dictionaries
        try:
            return make_json_serializable(obj.__dict__)
        except:
            # If that fails, try string representation
            return str(obj)
    else:
        # Default to string representation for other types
        try:
            return str(obj)
        except:
            return "Non-serializable object"

def initialize_checkpoint(case: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Initialize a new case with checkpoint metadata.
    
    Args:
        case: Optional existing case dictionary to initialize with checkpoint metadata
        
    Returns:
        Dictionary containing the case with checkpoint metadata
    """
    checkpoint_dir = get_checkpoint_dir()
    
    if case is None:
        case = {}
        
    # Generate a unique ID if not present
    if "case_id" not in case:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        case["case_id"] = f"case-{timestamp}-{random_suffix}"
    
    # Set up checkpoint information
    case["checkpoint_file"] = str(checkpoint_dir / f"case_{case['case_id']}.json")
    case["checkpoint_history"] = []
    case["last_checkpoint"] = None
    case["creation_timestamp"] = datetime.now().isoformat()
    
    # Initial save
    save_checkpoint(case, "initialized")
    
    return case

def save_checkpoint(case: Dict[str, Any], stage: str) -> Dict[str, Any]:
    """
    Save a checkpoint of the case generation process.
    
    Args:
        case: The case dictionary to save
        stage: The current stage name (e.g., "draft", "analyzed")
        
    Returns:
        The case dictionary (same as input)
    """
    # Make a copy to avoid modifying the original
    case_copy = case.copy()
    
    # Update checkpoint metadata
    case_copy["last_checkpoint"] = stage
    case_copy["checkpoint_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Track checkpoint history
    if "checkpoint_history" not in case_copy:
        case_copy["checkpoint_history"] = []
    
    case_copy["checkpoint_history"].append({
        "stage": stage,
        "timestamp": datetime.now().isoformat()
    })
    
    # Make JSON serializable
    case_copy = make_json_serializable(case_copy)
    
    # Ensure checkpoint file path is set
    if "checkpoint_file" not in case_copy:
        checkpoint_dir = get_checkpoint_dir()
        case_copy["checkpoint_file"] = str(checkpoint_dir / f"case_{case_copy['case_id']}.json")
    
    # Ensure checkpoint directory exists
    os.makedirs(os.path.dirname(case_copy["checkpoint_file"]), exist_ok=True)
    
    # Save to file
    with open(case_copy["checkpoint_file"], "w", encoding="utf-8") as f:
        json.dump(case_copy, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Checkpoint saved: {stage}")
    
    # Update the original case with checkpoint history
    case["checkpoint_history"] = case_copy["checkpoint_history"]
    case["last_checkpoint"] = stage
    case["checkpoint_time"] = case_copy["checkpoint_time"]
    
    return case

def load_checkpoint(case_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load a case from a checkpoint file.
    
    Args:
        case_id: Optional ID of the case to load. If None, loads the most recent checkpoint.
        
    Returns:
        The loaded case dictionary, or None if no checkpoint was found
    """
    checkpoint_dir = get_checkpoint_dir()
    
    if case_id:
        # Load specific case
        checkpoint_file = checkpoint_dir / f"case_{case_id}.json"
        if checkpoint_file.exists():
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                case = json.load(f)
                print(f"✓ Loaded checkpoint for case {case_id}")
                print(f"  Last stage: {case.get('last_checkpoint', 'unknown')}")
                return case
        else:
            print(f"⚠️ No checkpoint found for case ID: {case_id}")
            return None
    else:
        # Find most recent checkpoint
        checkpoint_files = list(checkpoint_dir.glob("case_*.json"))
        if not checkpoint_files:
            print("⚠️ No checkpoints found")
            return None
        
        # Sort by modification time (most recent first)
        checkpoint_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Load most recent checkpoint
        with open(checkpoint_files[0], "r", encoding="utf-8") as f:
            case = json.load(f)
            print(f"✓ Loaded most recent checkpoint: {checkpoint_files[0].name}")
            print(f"  Last stage: {case.get('last_checkpoint', 'unknown')}")
            return case

def list_checkpoints(limit: int = 10, include_completed: bool = False) -> List[Dict[str, Any]]:
    """
    List available checkpoints with their status.
    
    Args:
        limit: Maximum number of checkpoints to list
        include_completed: Whether to include completed cases
        
    Returns:
        List of dictionaries with checkpoint information
    """
    checkpoint_dir = get_checkpoint_dir()
    checkpoint_files = list(checkpoint_dir.glob("case_*.json"))
    
    if not checkpoint_files:
        print("No checkpoints found")
        return []
    
    # Sort by modification time (most recent first)
    checkpoint_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    results = []
    for file in checkpoint_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                case = json.load(f)
                
                # Skip completed cases if requested
                if not include_completed and case.get('last_checkpoint') == 'completed':
                    continue
                    
                results.append({
                    "case_id": case.get("case_id", "unknown"),
                    "last_stage": case.get("last_checkpoint", "unknown"),
                    "title": case.get("title", "Untitled Case"),
                    "created": case.get("creation_timestamp", "unknown"),
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                    "checkpoint_file": str(file)
                })
                
                if len(results) >= limit:
                    break
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # Print summary table
    if results:
        print(f"Found {len(results)} checkpoints:")
        for i, r in enumerate(results):
            print(f"{i+1}. [{r['last_stage']}] {r['title']} ({r['modified']})")
    else:
        print(f"No {'active' if not include_completed else ''} checkpoints found")
    
    return results

def delete_checkpoint(case_id: str) -> bool:
    """
    Delete a checkpoint file for a specific case.
    
    Args:
        case_id: ID of the case whose checkpoint should be deleted
        
    Returns:
        True if deletion was successful, False otherwise
    """
    checkpoint_dir = get_checkpoint_dir()
    checkpoint_file = checkpoint_dir / f"case_{case_id}.json"
    
    if checkpoint_file.exists():
        try:
            checkpoint_file.unlink()
            print(f"✓ Deleted checkpoint for case {case_id}")
            return True
        except Exception as e:
            print(f"⚠️ Failed to delete checkpoint for case {case_id}: {e}")
            return False
    else:
        print(f"⚠️ No checkpoint found for case ID: {case_id}")
        return False

def cleanup_checkpoints(keep_days: int = 30, keep_completed: bool = True) -> int:
    """
    Clean up old checkpoint files.
    
    Args:
        keep_days: Number of days to keep checkpoints
        keep_completed: Whether to keep completed checkpoints regardless of age
        
    Returns:
        Number of checkpoints deleted
    """
    checkpoint_dir = get_checkpoint_dir()
    checkpoint_files = list(checkpoint_dir.glob("case_*.json"))
    
    if not checkpoint_files:
        print("No checkpoints found")
        return 0
    
    now = datetime.now()
    cutoff = now.timestamp() - (keep_days * 24 * 60 * 60)
    deleted_count = 0
    
    for file in checkpoint_files:
        try:
            # Check file age
            mtime = file.stat().st_mtime
            if mtime < cutoff:
                # Check if completed and should be kept
                if keep_completed:
                    with open(file, "r", encoding="utf-8") as f:
                        case = json.load(f)
                        if case.get('last_checkpoint') == 'completed':
                            continue
                
                # Delete the file
                file.unlink()
                deleted_count += 1
                
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} old checkpoints")
    else:
        print("No checkpoints were deleted")
    
    return deleted_count

# Add to checkpointing.py
def convert_notebook_checkpoint_to_case(checkpoint_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a checkpoint from the notebook format to the new Case format.
    
    This helper function assists in migrating from the old notebook-based
    checkpoints to the new object-oriented approach.
    
    Args:
        checkpoint_dict: Checkpoint dictionary from notebook format
        
    Returns:
        Converted case dictionary compatible with new system
    """
    from ..models.case import Case, CaseStage
    
    # Create a new Case instance
    case = Case(
        case_id=checkpoint_dict.get('case_id', str(uuid.uuid4())),
        title=checkpoint_dict.get('title', 'Migrated Case'),
    )
    
    # Map stage
    stage_mapping = {
        'initialized': CaseStage.INITIALIZED,
        'draft': CaseStage.DRAFT,
        'analyzed': CaseStage.ANALYZED,
        'datapoints_retrieved': CaseStage.DATAPOINTS_RETRIEVED,
        'enhanced': CaseStage.ENHANCED,
        'completed': CaseStage.COMPLETED,
        'failed': CaseStage.FAILED
    }
    
    last_checkpoint = checkpoint_dict.get('last_checkpoint', 'initialized')
    case.current_stage = stage_mapping.get(last_checkpoint, CaseStage.INITIALIZED)
    
    # Copy all applicable fields
    case.draft_case = checkpoint_dict.get('draft_case', '')
    case.analysis = checkpoint_dict.get('analysis', '')
    case.enhanced_case = checkpoint_dict.get('enhanced_case', '')
    case.solution = checkpoint_dict.get('solution', '')
    case.search_queries = checkpoint_dict.get('search_queries', [])
    case.keywords = checkpoint_dict.get('keywords', [])
    case.relevant_datapoints = checkpoint_dict.get('relevant_datapoints', [])
    case.domain_guideline = checkpoint_dict.get('domain_guideline')
    case.generation_metadata = checkpoint_dict.get('generation_metadata', {})
    
    # Convert completion status
    case.draft_complete = checkpoint_dict.get('draft_complete', False)
    case.analysis_complete = checkpoint_dict.get('analysis_complete', False)
    case.datapoints_complete = checkpoint_dict.get('datapoints_complete', False)
    case.enhancement_complete = checkpoint_dict.get('enhancement_complete', False)
    case.solution_complete = checkpoint_dict.get('solution_complete', False)
    
    return case.to_dict()

if __name__ == "__main__":
    # Simple test/demo when run directly
    print("Checkpoint System Test")
    print("-" * 40)
    
    print("\nListing existing checkpoints:")
    checkpoints = list_checkpoints(limit=5, include_completed=True)
    
    print("\nCreating a test checkpoint:")
    test_case = initialize_checkpoint()
    test_case["title"] = "Test Case for Checkpoint System"
    test_case["test_data"] = "This is a test"
    
    print("\nSaving checkpoint:")
    save_checkpoint(test_case, "test")
    
    print("\nLoading checkpoint:")
    loaded_case = load_checkpoint(test_case["case_id"])
    
    print("\nDeleting test checkpoint:")
    delete_checkpoint(test_case["case_id"])
    
    print("\nCheckpoint system test complete")