"""
Logger module for maritime case generation pipeline.

This module provides structured logging functionality for tracking the progress,
performance, and errors during the case generation process.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class CaseGenerationLogger:
    """
    Logger for case generation pipeline with JSON file output.
    
    This class provides structured logging capabilities for tracking the 
    case generation process, including stage timings, LLM requests/responses,
    data retrievals, and errors.
    
    Attributes:
        case_id: Unique identifier for the case being generated
        log_dir: Directory for storing log files
        log_file: Path to the specific log file for this case
        start_time: Timestamp when logging was initialized
        stage_timings: Dictionary mapping stage names to their durations
        stage_start_time: Timestamp when the current stage started
        current_stage: Name of the current processing stage
    """
    
    def __init__(self, case_id: Optional[str] = None, log_dir: Union[str, Path] = None):
        """
        Initialize a new logger for case generation.
        
        Args:
            case_id: Optional ID for the case. If not provided, a UUID will be generated.
            log_dir: Directory path for log files. Defaults to "../Data/Logs".
        """
        self.case_id = case_id or str(uuid.uuid4())[:8]
        self.log_dir = Path(log_dir or Path(__file__).parents[2] / "Data" / "Logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log filename with case ID
        self.log_file = self.log_dir / f"case_{self.case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
        # Initialize metrics
        self.start_time = datetime.now()
        self.stage_timings: Dict[str, float] = {}
        self.stage_start_time: Optional[datetime] = None
        self.current_stage: Optional[str] = None
        
        # Initialize the log file with header
        self.info("LOGGING_INITIALIZED", "Case generation logging started", {
            "case_id": self.case_id,
            "log_file": str(self.log_file),
            "timestamp": self.start_time.isoformat()
        })
        
        print(f"✓ Logging initialized for case {self.case_id}")
    
    def _log(self, level: str, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """
        Write a log entry to the log file.
        
        Args:
            level: Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
            event_type: Type of event being logged
            message: Human-readable description of the event
            data: Optional dictionary of additional data to include in the log
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "case_id": self.case_id,
            "event": event_type,
            "message": message,
            "stage": self.current_stage
        }
        
        # Add additional data if provided
        if data:
            log_entry["data"] = data
        
        # Write to log file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def start_stage(self, stage_name: str):
        """
        Start timing a new stage of the pipeline.
        
        Args:
            stage_name: Name of the stage being started
        """
        self.current_stage = stage_name
        self.stage_start_time = datetime.now()
        self.info(f"STAGE_START", f"Starting stage: {stage_name}")
    
    def end_stage(self, success: bool = True, result_summary: Optional[Dict[str, Any]] = None):
        """
        End timing for the current stage and log results.
        
        Args:
            success: Whether the stage completed successfully
            result_summary: Optional summary of stage results
        """
        if not self.current_stage or not self.stage_start_time:
            return
        
        duration = (datetime.now() - self.stage_start_time).total_seconds()
        self.stage_timings[self.current_stage] = duration
        
        log_data = {
            "duration_seconds": duration,
            "success": success
        }
        
        if result_summary:
            log_data["result_summary"] = result_summary
            
        event_type = "STAGE_COMPLETE" if success else "STAGE_FAILED"
        self.info(
            event_type, 
            f"Stage {self.current_stage} completed in {duration:.2f}s",
            log_data
        )
    
    def debug(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log debug information."""
        self._log("DEBUG", event_type, message, data)
    
    def info(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log informational message."""
        self._log("INFO", event_type, message, data)
    
    def warning(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._log("WARNING", event_type, message, data)
    
    def error(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self._log("ERROR", event_type, message, data)
    
    def critical(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log critical error message."""
        self._log("CRITICAL", event_type, message, data)
    
    def log_llm_request(self, model: str, prompt_length: int, 
                      temperature: Optional[float] = None, 
                      max_tokens: Optional[int] = None):
        """
        Log an LLM request being made.
        
        Args:
            model: Name of the LLM model
            prompt_length: Length of the prompt in characters
            temperature: Optional temperature parameter
            max_tokens: Optional max tokens parameter
        """
        self.debug("LLM_REQUEST", f"Request to {model}", {
            "model": model,
            "prompt_length": prompt_length,
            "temperature": temperature,
            "max_tokens": max_tokens
        })
    
    def log_llm_response(self, model: str, response_length: int, duration: float):
        """
        Log an LLM response received.
        
        Args:
            model: Name of the LLM model
            response_length: Length of the response in characters
            duration: Time taken to receive the response in seconds
        """
        self.debug("LLM_RESPONSE", f"Response from {model}", {
            "model": model,
            "response_length": response_length,
            "duration_seconds": duration
        })
    
    def log_data_retrieval(self, query: str, results_count: int, duration: Optional[float] = None):
        """
        Log data retrieval from vector DB.
        
        Args:
            query: Search query used for retrieval
            results_count: Number of results retrieved
            duration: Optional time taken for retrieval in seconds
        """
        self.debug("DATA_RETRIEVAL", f"Retrieved {results_count} results", {
            "query": query[:100] + "..." if len(query) > 100 else query,
            "results_count": results_count,
            "duration_seconds": duration
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the logging activity.
        
        Returns:
            Dictionary containing logging summary metrics
        """
        if self.stage_timings:
            total_duration = sum(self.stage_timings.values())
            stages = len(self.stage_timings)
        else:
            total_duration = 0
            stages = 0
            
        return {
            "case_id": self.case_id,
            "log_file": str(self.log_file),
            "total_duration": total_duration,
            "stages_completed": stages,
            "stage_timings": self.stage_timings
        }
    
    def finalize(self) -> Dict[str, Any]:
        """
        Log final summary and completion.
        
        Returns:
            Dictionary containing the final logging summary
        """
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        self.info("GENERATION_COMPLETE", f"Case generation completed in {total_duration:.2f}s", {
            "total_duration_seconds": total_duration,
            "stage_timings": self.stage_timings
        })
        
        return self.get_summary()# Logging functionality implementation
