# API endpoints implementation
"""
API endpoints for the Maritime Case Generator.

This module provides REST API endpoints for interacting with the case generation system,
allowing for case creation, retrieval, and management through HTTP requests.
"""

import os
import time
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Query, Path as PathParam
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import project modules
from ..pipeline.runner import run_case_generation_pipeline
from ..pipeline.checkpointing import list_checkpoints, load_checkpoint, delete_checkpoint, cleanup_checkpoints
from ..utils.vector_db import test_connection as test_db_connection
from ..utils.llm import test_llm_connection

# Create FastAPI app
app = FastAPI(
    title="Maritime Logistics Case Generator API",
    description="API for generating maritime logistics case studies with solutions",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can be set to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background tasks store
running_tasks = {}

# Pydantic models for request/response validation
class GenerateCaseRequest(BaseModel):
    """Request model for case generation"""
    focus_area: Optional[str] = Field(None, description="Optional focus area for the case")
    region: Optional[str] = Field(None, description="Optional geographical region for the case")
    generate_teaching_materials: bool = Field(False, description="Whether to generate teaching notes")
    model: Optional[str] = Field(None, description="Override LLM model")
    debug: bool = Field(True, description="Enable debug output")

class CheckpointListResponse(BaseModel):
    """Response model for checkpoint listing"""
    checkpoints: List[Dict[str, Any]]
    count: int

class CaseDetailResponse(BaseModel):
    """Response model for case details"""
    case_id: str
    title: str
    stage: str
    created: str
    content: Dict[str, Any]

class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
class SystemStatusResponse(BaseModel):
    """Response model for system status"""
    db_connection: bool
    llm_connection: bool
    available_models: List[str]
    total_cases: int
    db_collections: List[str]


# Helper functions for endpoint implementation
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a background task"""
    if task_id not in running_tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return running_tasks[task_id]

def start_case_generation(
    task_id: str, 
    resume_from: Optional[str] = None,
    generate_teaching_materials: bool = False,
    model: Optional[str] = None,
    debug: bool = True
):
    """Start case generation in the background"""
    try:
        # Initialize task status
        running_tasks[task_id] = {
            "task_id": task_id,
            "status": "running",
            "progress": 0.0,
            "message": "Starting case generation...",
            "result": None
        }
        
        # Run the pipeline
        result = run_case_generation_pipeline(
            resume_from=resume_from,
            save_checkpoints=True,
            debug=debug,
            generate_teaching_materials=generate_teaching_materials,
            llm_model=model
        )
        
        # Update task status with success
        running_tasks[task_id].update({
            "status": "completed",
            "progress": 100.0,
            "message": f"Generated case: {result.get('title', 'Untitled')}",
            "result": {
                "case_id": result.get("case_id"),
                "title": result.get("title", "Untitled Case"),
                "final_path": result.get("final_path", "")
            }
        })
        
    except Exception as e:
        # Update task status with failure
        running_tasks[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "message": f"Case generation failed: {str(e)}"
        })

# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Maritime Logistics Case Generator API",
        "version": "1.0.0",
        "description": "API for generating maritime logistics case studies with solutions"
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/status", response_model=SystemStatusResponse, tags=["General"])
async def system_status():
    """Get system status including database and LLM connections"""
    from ..pipeline.checkpointing import list_checkpoints

    # Test connections
    db_status = test_db_connection()
    llm_status = test_llm_connection()
    
    # Count available cases
    checkpoints = list_checkpoints(limit=1000, include_completed=True)
    
    # Get DB collections
    db_collections = []
    try:
        from ..utils.vector_db import get_qdrant_client
        client = get_qdrant_client()
        collections = client.get_collections().collections
        db_collections = [c.name for c in collections]
    except Exception:
        pass
    
    # Determine available models
    available_models = []
    if llm_status.get("success", False):
        available_models = ["gemini-2.0-flash-exp", "gemini-2.0-pro", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    return {
        "db_connection": db_status,
        "llm_connection": llm_status.get("success", False),
        "available_models": available_models,
        "total_cases": len(checkpoints),
        "db_collections": db_collections
    }

@app.post("/cases", tags=["Case Generation"])
async def generate_case(
    request: GenerateCaseRequest,
    background_tasks: BackgroundTasks
):
    """
    Start generating a new case study
    
    This endpoint begins case generation as a background task and returns a task ID
    that can be used to check the status of the generation process.
    """
    # Generate a task ID
    task_id = f"task_{int(time.time())}_{os.urandom(4).hex()}"
    
    # Start the task in the background
    background_tasks.add_task(
        start_case_generation,
        task_id=task_id,
        generate_teaching_materials=request.generate_teaching_materials,
        model=request.model,
        debug=request.debug
    )
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Case generation started in the background"
    }

@app.post("/cases/resume/{case_id}", tags=["Case Generation"])
async def resume_case_generation(
    case_id: str = PathParam(..., description="ID of the case to resume"),
    background_tasks: BackgroundTasks = None,
    generate_teaching_materials: bool = Query(False, description="Whether to generate teaching notes"),
    model: Optional[str] = Query(None, description="Override LLM model"),
    debug: bool = Query(True, description="Enable debug output")
):
    """
    Resume case generation from a checkpoint
    
    This endpoint resumes a previously interrupted case generation process
    from the last checkpoint.
    """
    # Check if the checkpoint exists
    checkpoint = load_checkpoint(case_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    # Generate a task ID
    task_id = f"resume_{case_id}_{int(time.time())}"
    
    # Start the task in the background
    background_tasks.add_task(
        start_case_generation,
        task_id=task_id,
        resume_from=case_id,
        generate_teaching_materials=generate_teaching_materials,
        model=model,
        debug=debug
    )
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": f"Resuming case {case_id} in the background",
        "case_id": case_id
    }

@app.get("/tasks/{task_id}", response_model=TaskStatusResponse, tags=["Case Generation"])
async def get_task_status_endpoint(
    task_id: str = PathParam(..., description="ID of the task to check")
):
    """
    Check the status of a background task
    
    This endpoint returns the current status of a case generation task,
    including progress, any error messages, and the result when complete.
    """
    status = get_task_status(task_id)
    return status

@app.get("/checkpoints", response_model=CheckpointListResponse, tags=["Checkpoint Management"])
async def list_checkpoints_endpoint(
    limit: int = Query(10, description="Maximum number of checkpoints to return"),
    include_completed: bool = Query(False, description="Include completed cases")
):
    """
    List available checkpoints
    
    This endpoint returns a list of available checkpoints, which can be used
    to resume case generation or view previously generated cases.
    """
    checkpoints = list_checkpoints(limit=limit, include_completed=include_completed)
    return {"checkpoints": checkpoints, "count": len(checkpoints)}

@app.get("/cases/{case_id}", response_model=CaseDetailResponse, tags=["Case Management"])
async def get_case(
    case_id: str = PathParam(..., description="ID of the case to retrieve")
):
    """
    Get details of a specific case
    
    This endpoint returns the full details of a generated case, including
    the case text, solution, and any associated metadata.
    """
    case = load_checkpoint(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    # Extract only the relevant information for the response
    return {
        "case_id": case.get("case_id", ""),
        "title": case.get("title", "Untitled Case"),
        "stage": case.get("last_checkpoint", "unknown"),
        "created": case.get("creation_timestamp", ""),
        "content": case
    }

@app.delete("/cases/{case_id}", tags=["Case Management"])
async def delete_case(
    case_id: str = PathParam(..., description="ID of the case to delete")
):
    """
    Delete a case
    
    This endpoint deletes a case and its checkpoint file. This operation cannot be undone.
    """
    success = delete_checkpoint(case_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    return {"success": True, "message": f"Case {case_id} deleted"}

@app.post("/checkpoints/cleanup", tags=["Checkpoint Management"])
async def cleanup_checkpoints_endpoint(
    keep_days: int = Query(30, description="Number of days to keep checkpoints"),
    keep_completed: bool = Query(True, description="Whether to keep completed cases")
):
    """
    Clean up old checkpoints
    
    This endpoint deletes old checkpoint files based on age and completion status.
    """
    deleted_count = cleanup_checkpoints(keep_days=keep_days, keep_completed=keep_completed)
    
    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Deleted {deleted_count} old checkpoints"
    }

@app.get("/examples", tags=["Reference Data"])
async def list_examples(limit: int = Query(10, description="Maximum number of examples to return")):
    """
    List example cases
    
    This endpoint returns a list of example cases from the vector database.
    """
    from ..utils.vector_db import get_qdrant_client
    from qdrant_client.http import models
    
    client = get_qdrant_client()
    
    try:
        # Get examples from the vector database
        examples, _ = client.scroll(
            collection_name="case_generation_references",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="content_type",
                        match=models.MatchValue(value="example")
                    )
                ]
            ),
            limit=limit,
            with_payload=True
        )
        
        return {
            "examples": [example.payload for example in examples],
            "count": len(examples)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving examples: {str(e)}")

@app.get("/guidelines", tags=["Reference Data"])
async def list_guidelines(
    guideline_type: Optional[str] = Query(None, description="Filter by guideline type")
):
    """
    List guidelines
    
    This endpoint returns a list of guidelines from the vector database,
    optionally filtered by type.
    """
    from ..utils.vector_db import get_qdrant_client
    from qdrant_client.http import models
    
    client = get_qdrant_client()
    
    try:
        # Build filter conditions
        filter_conditions = [
            models.FieldCondition(
                key="content_type",
                match=models.MatchValue(value="guideline")
            )
        ]
        
        # Add guideline type filter if specified
        if guideline_type:
            filter_conditions.append(
                models.FieldCondition(
                    key="guideline_type",
                    match=models.MatchValue(value=guideline_type)
                )
            )
        
        # Get guidelines from the vector database
        guidelines, _ = client.scroll(
            collection_name="case_generation_references",
            scroll_filter=models.Filter(must=filter_conditions),
            limit=100,
            with_payload=True
        )
        
        return {
            "guidelines": [guideline.payload for guideline in guidelines],
            "count": len(guidelines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving guidelines: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)