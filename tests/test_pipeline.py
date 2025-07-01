"""
Tests for the Maritime Logistics Case Generator pipeline.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock, mock_open

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parents[1]))

# We need to patch google.generativeai BEFORE it gets imported anywhere
with patch('google.generativeai.configure'), patch('google.generativeai.GenerativeModel'):
    from src.pipeline.runner import run_case_generation_pipeline, log_stage_error, save_final_case
    from src.pipeline.checkpointing import initialize_checkpoint, save_checkpoint, load_checkpoint

# Mock sample data
MOCK_EXAMPLE = {
    "title": "Mock Example Case",
    "summary": "A sample case about maritime logistics documentation requirements."
}

MOCK_DRAFT = "This is a mock case draft about container shipping between Rotterdam and Singapore."

MOCK_ANALYSIS = """
## Case Analysis
This case covers international shipping documentation.
"""

MOCK_DATAPOINTS = [
    {"id": "dp1", "title": "Documentation Requirements", "content": "Sample content about documentation."},
    {"id": "dp2", "title": "Customs Procedures", "content": "Sample content about customs."}
]

MOCK_ENHANCED = "This is an enhanced case with specific details about documentation requirements."

MOCK_SOLUTION = """
## Executive Summary
This case involves documentation challenges.
"""

# Mock Qdrant client
class MockQdrantClient:
    def __init__(self, *args, **kwargs):
        pass
    
    def scroll(self, *args, **kwargs):
        mock_points = [MagicMock(payload=MOCK_EXAMPLE)]
        return mock_points, None
    
    def search(self, *args, **kwargs):
        return [MagicMock(payload=dp) for dp in MOCK_DATAPOINTS]
    
    def query_points(self, *args, **kwargs):
        return [MagicMock(payload=dp) for dp in MOCK_DATAPOINTS]

@pytest.fixture
def temp_checkpoint_dir():
    """Create a temporary checkpoint directory for testing."""
    temp_dir = tempfile.mkdtemp()
    with patch('src.pipeline.checkpointing.get_checkpoint_dir') as mock_get_dir:
        mock_get_dir.return_value = Path(temp_dir)
        yield temp_dir
    shutil.rmtree(temp_dir)

# Mock the entire pipeline process
@pytest.fixture
def mock_pipeline_components():
    with patch('src.utils.llm.generate_text') as mock_generate_text, \
         patch('src.utils.vector_db.get_qdrant_client') as mock_db_client, \
         patch('google.generativeai.configure') as mock_google_configure, \
         patch('google.auth.default') as mock_auth_default, \
         patch('src.stages.draft_generation.select_random_example', return_value=MOCK_EXAMPLE) as mock_select, \
         patch('src.stages.draft_generation.generate_case_draft', return_value={"draft_case": MOCK_DRAFT, "draft_complete": True}) as mock_generate, \
         patch('src.stages.analysis.analyze_case_draft', return_value={"draft_case": MOCK_DRAFT, "analysis": MOCK_ANALYSIS, "analysis_complete": True}) as mock_analyze, \
         patch('src.stages.analysis.extract_queries_and_keywords', return_value=(["query1", "query2"], ["keyword1", "keyword2"])) as mock_extract, \
         patch('src.stages.datapoint_retrieval.retrieve_relevant_datapoints', return_value={
             "draft_case": MOCK_DRAFT, 
             "analysis": MOCK_ANALYSIS,
             "relevant_datapoints": MOCK_DATAPOINTS,
             "datapoints_complete": True
         }) as mock_retrieve, \
         patch('src.stages.enhancement.enhance_case_with_context', return_value={
             "draft_case": MOCK_DRAFT, 
             "analysis": MOCK_ANALYSIS,
             "relevant_datapoints": MOCK_DATAPOINTS,
             "enhanced_case": MOCK_ENHANCED,
             "title": "Test Case",
             "enhancement_complete": True
         }) as mock_enhance, \
         patch('src.stages.solution.develop_solution', return_value={
             "draft_case": MOCK_DRAFT, 
             "analysis": MOCK_ANALYSIS,
             "relevant_datapoints": MOCK_DATAPOINTS,
             "enhanced_case": MOCK_ENHANCED,
             "title": "Test Case",
             "solution": MOCK_SOLUTION,
             "solution_complete": True
         }) as mock_solution:
            
            # Configure mocks
            mock_generate_text.return_value = "Mock generated text"
            mock_db_client.return_value = MockQdrantClient()
            
            yield {
                "generate_text": mock_generate_text,
                "db_client": mock_db_client,
                "select": mock_select,
                "generate": mock_generate,
                "analyze": mock_analyze,
                "extract": mock_extract,
                "retrieve": mock_retrieve,
                "enhance": mock_enhance,
                "solution": mock_solution
            }

class TestPipeline:
    """Tests for the complete pipeline functionality."""
    
    def test_full_pipeline_run(self, mock_pipeline_components, temp_checkpoint_dir):
        """Test a complete run of the pipeline with mocked components."""
        # Set up file path to prevent file system issues
        mock_file_path = Path(temp_checkpoint_dir) / "test_case.json"
        
        # Run pipeline with mocks
        with patch('src.models.logger.CaseGenerationLogger'), \
             patch('src.pipeline.runner.save_final_case') as mock_save, \
             patch('pathlib.Path.open', mock_open()), \
             patch('builtins.open', mock_open()):
            
            mock_save.return_value = mock_file_path
            
            # Override direct module access to prevent real API calls
            with patch.dict('sys.modules', {'google.generativeai': MagicMock()}):
                result = run_case_generation_pipeline(
                    debug=True,
                    save_checkpoints=True,
                )
        
        # Check that the pipeline completed successfully
        assert result is not None
        assert "solution_complete" in result
        assert result["solution_complete"] is True
        
        # Verify stage calls
        mocks = mock_pipeline_components
        mocks["select"].assert_called_once()
        mocks["generate"].assert_called_once()
        mocks["analyze"].assert_called_once()
        mocks["retrieve"].assert_called_once()
        mocks["enhance"].assert_called_once()
        mocks["solution"].assert_called_once()
    
    def test_pipeline_resume(self, mock_pipeline_components, temp_checkpoint_dir):
        """Test resuming the pipeline from a checkpoint."""
        # Create a mock partially completed case
        partial_case = {
            "case_id": "test-case-123",
            "draft_case": MOCK_DRAFT,
            "analysis": MOCK_ANALYSIS,
            "relevant_datapoints": MOCK_DATAPOINTS,
            "draft_complete": True,
            "analysis_complete": True,
            "datapoints_complete": True,
            "last_checkpoint": "datapoints_retrieved",
            "logger": None  # Needed to avoid AttributeError
        }
        
        # Run with mocks
        with patch('src.pipeline.checkpointing.load_checkpoint', return_value=partial_case), \
             patch('src.models.logger.CaseGenerationLogger'), \
             patch('src.pipeline.runner.save_final_case') as mock_save, \
             patch('pathlib.Path.open', mock_open()), \
             patch('builtins.open', mock_open()):
            
            mock_save.return_value = Path(temp_checkpoint_dir) / "test_case.json"
            
            # Override direct module access to prevent real API calls
            with patch.dict('sys.modules', {'google.generativeai': MagicMock()}):
                result = run_case_generation_pipeline(
                    resume_from="test-case-123",
                    debug=True,
                    save_checkpoints=True,
                )
        
        # Check that the pipeline resumed and completed correctly
        assert result is not None
        assert "solution_complete" in result
        
        # Only these stages should be called when resuming from datapoints_retrieved
        mocks = mock_pipeline_components
        mocks["enhance"].assert_called_once()
        mocks["solution"].assert_called_once()
    
    def test_pipeline_error_handling(self, temp_checkpoint_dir):
        """Test that the pipeline handles errors gracefully."""
        # Configure mocks specifically for this test
        with patch('src.utils.llm.generate_text', return_value="Mock text"), \
             patch('src.utils.vector_db.get_qdrant_client', return_value=MockQdrantClient()), \
             patch('src.stages.draft_generation.select_random_example', return_value=MOCK_EXAMPLE) as mock_select, \
             patch('src.stages.draft_generation.generate_case_draft', side_effect=Exception("Mock error")) as mock_generate, \
             patch('src.models.logger.CaseGenerationLogger'), \
             patch('pathlib.Path.open', mock_open()), \
             patch('builtins.open', mock_open()), \
             patch.dict('sys.modules', {'google.generativeai': MagicMock()}):
            
            result = run_case_generation_pipeline(
                debug=True,
                save_checkpoints=True,
            )
        
        # Check that the pipeline caught the error and returned a partially completed case
        assert result is not None
        assert "draft_complete" not in result or result["draft_complete"] is False
        
        # Verify stage calls
        mock_select.assert_called_once()
        mock_generate.assert_called_once()
    
    def test_log_stage_error(self):
        """Test the error logging function."""
        # Create a test case with a mock logger
        test_case = {"logger": MagicMock()}
        
        # Create a test error
        test_error = ValueError("Test error message")
        
        # Log the error
        result = log_stage_error(test_case, "test_stage", test_error)
        
        # Verify the result
        assert "Test error message" in result
        
        # Verify logger calls
        test_case["logger"].error.assert_called_once()
        test_case["logger"].end_stage.assert_called_once()
    
    def test_save_final_case(self, temp_checkpoint_dir):
        """Test saving the final case output."""
        # Create output directory
        output_dir = Path(temp_checkpoint_dir) / "Output" / "Generated_Cases"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock the path to the output directory
        with patch('src.pipeline.runner.Path') as mock_path:
            # Configure mock to return our temp directory
            mock_path.return_value.parents.__getitem__.return_value = Path(temp_checkpoint_dir)
            
            # Create a test case and mock the serialization function
            test_case = {"title": "Test Case", "case_id": "test-123"}
            
            # Use the proper mock_open pattern
            with patch('src.pipeline.checkpointing.make_json_serializable', return_value=test_case), \
                 patch('builtins.open', mock_open()) as m:
                result = save_final_case(test_case)
            
            # Verify the result is a Path
            assert isinstance(result, Path)
            # Verify file operations
            m.assert_called_once()


if __name__ == "__main__":
    pytest.main(["-v", __file__])