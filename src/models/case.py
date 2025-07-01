# Case data model implementation
"""
Case data model for the Maritime Logistics Case Generator.

This module defines the core Case class that represents a maritime logistics case study
throughout its generation lifecycle, from initialization to completion.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import uuid
import json
from copy import deepcopy


class CaseStage(Enum):
    """Enumeration of possible case generation stages."""
    INITIALIZED = "initialized"
    DRAFT = "draft"
    ANALYZED = "analyzed"
    DATAPOINTS_RETRIEVED = "datapoints_retrieved"
    ENHANCED = "enhanced"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Case:
    """
    Represents a maritime logistics case study throughout its generation lifecycle.
    
    This class tracks the state, content, and metadata of a case as it progresses
    through the generation pipeline stages.
    """
    # Core identifiers
    case_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled Case"
    
    # Stage tracking
    current_stage: CaseStage = CaseStage.INITIALIZED
    last_checkpoint: str = "initialized"
    
    # Stage completion status
    draft_complete: bool = False
    analysis_complete: bool = False
    datapoints_complete: bool = False
    enhancement_complete: bool = False
    solution_complete: bool = False
    
    # Case content
    draft_case: str = ""
    analysis: str = ""
    enhanced_case: str = ""
    solution: str = ""
    
    # Example and inspiration
    example_inspiration: str = ""
    example_filename: str = ""
    
    # Search queries and datapoints
    search_queries: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    relevant_datapoints: List[Dict[str, Any]] = field(default_factory=list)
    
    # Domain guidance
    domain_guideline: Optional[str] = None
    
    # Metadata fields
    creation_time: str = field(default_factory=lambda: datetime.now().isoformat())
    creation_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    pipeline_version: str = "2.0"
    final_path: Optional[str] = None
    
    # Additional metadata
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    enhancement_metadata: Dict[str, Any] = field(default_factory=dict)
    solution_metadata: Dict[str, Any] = field(default_factory=dict)
    search_metadata: Dict[str, Any] = field(default_factory=dict)
    log_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Checkpoint information
    checkpoint_file: Optional[str] = None
    checkpoint_history: List[str] = field(default_factory=list)
    
    # Error tracking
    error: Optional[str] = None
    error_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def advance_stage(self, new_stage: Union[CaseStage, str]) -> None:
        """
        Advance the case to a new stage and update completion status.
        
        Args:
            new_stage: The new stage to advance to
        """
        if isinstance(new_stage, str):
            try:
                new_stage = CaseStage(new_stage)
            except ValueError:
                raise ValueError(f"Invalid case stage: {new_stage}")
        
        self.current_stage = new_stage
        self.last_checkpoint = new_stage.value
        
        # Update completion status based on the new stage
        if new_stage == CaseStage.DRAFT:
            self.draft_complete = True
        elif new_stage == CaseStage.ANALYZED:
            self.analysis_complete = True
        elif new_stage == CaseStage.DATAPOINTS_RETRIEVED:
            self.datapoints_complete = True
        elif new_stage == CaseStage.ENHANCED:
            self.enhancement_complete = True
        elif new_stage == CaseStage.COMPLETED:
            self.solution_complete = True
    
    def is_complete(self) -> bool:
        """Check if the case is fully complete."""
        return (
            self.draft_complete and 
            self.analysis_complete and 
            self.datapoints_complete and 
            self.enhancement_complete and 
            self.solution_complete
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the case to a dictionary for serialization."""
        # Create a deep copy to avoid modifying the original
        case_dict = {}
        
        # Don't include any callables, modules, or complex objects
        for key, value in self.__dict__.items():
            if not key.startswith("_") and not callable(value):
                if isinstance(value, CaseStage):
                    case_dict[key] = value.value
                else:
                    case_dict[key] = value
        
        return case_dict
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the case to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Case":
        """Create a Case instance from a dictionary."""
        # Convert string stage to enum if needed
        if "current_stage" in data and isinstance(data["current_stage"], str):
            try:
                data["current_stage"] = CaseStage(data["current_stage"])
            except ValueError:
                data["current_stage"] = CaseStage.INITIALIZED
        
        # Filter out any keys that aren't in the Case dataclass
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Case":
        """Create a Case instance from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def load_from_file(cls, filepath: Union[str, Path]) -> "Case":
        """Load a case from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def save_to_file(self, filepath: Union[str, Path]) -> None:
        """Save the case to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    def update_metadata(self, llm_model: str, embedding_model: str) -> None:
        """Update the generation metadata."""
        self.generation_metadata = {
            "llm_model": llm_model,
            "embedding_model": embedding_model,
            "completion_time": datetime.now().isoformat(),
            "pipeline_version": self.pipeline_version
        }