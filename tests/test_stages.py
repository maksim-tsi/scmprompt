# Tests for the pipeline stages
"""
Unit tests for pipeline stages of the Maritime Case Generator.

These tests validate the functionality of individual pipeline stages,
ensuring each component works correctly in isolation.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add the project root to the Python path to ensure imports work
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.stages.draft_generation import select_random_example, generate_case_draft
from src.stages.analysis import analyze_case_draft, extract_queries_and_keywords
from src.stages.datapoint_retrieval import retrieve_relevant_datapoints
from src.stages.enhancement import enhance_case_with_context, find_relevant_guideline
from src.stages.solution import develop_solution

# Mock data for tests
MOCK_EXAMPLE_CASE = {
    "title": "Mock Example Case",
    "summary": "This is a mock example case for testing the draft generation stage.",
    "filename": "mock_example.md"
}

MOCK_DRAFT_CASE = {
    "draft_case": "This is a draft maritime logistics case involving container shipping between Shanghai and Hamburg.",
    "creation_date": "2025-03-28",
    "example_inspiration": "Mock Example Case"
}

MOCK_ANALYSIS = """
## Case Analysis
This is a basic maritime logistics case that needs more detail.

## Knowledge Gaps
- Specific regulations for container shipping
- Documentation requirements

## Search Queries
- Container shipping regulations
- Hamburg port requirements
- Bill of lading requirements

## Keywords
logistics, shipping, container, documentation, Hamburg, Shanghai
"""

MOCK_DATAPOINTS = [
    {
        "id": "dp1",
        "title": "Container Documentation",
        "content": "All containers must have proper documentation including bill of lading.",
        "search_score": 0.85
    },
    {
        "id": "dp2",
        "title": "Port of Hamburg Requirements",
        "content": "Vessels entering Hamburg must provide 24-hour notice.",
        "search_score": 0.78
    }
]


class TestDraftGeneration:
    """Tests for the draft generation stage."""
    
    @patch('src.stages.draft_generation.get_qdrant_client')
    def test_select_random_example(self, mock_get_client):
        """Test selecting a random example case."""
        # Configure the mock to return an appropriate value
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create a mock scroll response
        mock_client.scroll.return_value = ([MagicMock(payload=MOCK_EXAMPLE_CASE)], None)
        
        # Call the function
        result = select_random_example()
        
        # Validate the result
        assert isinstance(result, dict)
        assert "title" in result
        assert "summary" in result
    
    @patch('src.stages.draft_generation.generate_text')
    def test_generate_case_draft(self, mock_generate_text):
        """Test generating a case draft."""
        # Configure the mock
        mock_generate_text.return_value = "This is a generated case draft for testing."
        
        # Call the function
        result = generate_case_draft(MOCK_EXAMPLE_CASE)
        
        # Validate the result
        assert isinstance(result, dict)
        assert "draft_case" in result
        assert mock_generate_text.called
        assert result["example_inspiration"] == MOCK_EXAMPLE_CASE["title"]


class TestAnalysis:
    """Tests for the analysis stage."""
    
    @patch('src.stages.analysis.generate_text')
    def test_analyze_case_draft(self, mock_generate_text):
        """Test analyzing a case draft."""
        # Configure the mock
        mock_generate_text.return_value = MOCK_ANALYSIS
        
        # Call the function
        result = analyze_case_draft(MOCK_DRAFT_CASE)
        
        # Validate the result
        assert isinstance(result, dict)
        assert "analysis" in result
        assert result["analysis"] == MOCK_ANALYSIS
        assert mock_generate_text.called
    
    def test_extract_queries_and_keywords(self):
        """Test extracting queries and keywords from analysis."""
        # Prepare test data
        case = {
            "analysis": MOCK_ANALYSIS
        }
        
        # Call the function
        queries, keywords = extract_queries_and_keywords(case)
        
        # Validate the result
        assert isinstance(queries, list)
        assert isinstance(keywords, list)
        assert len(queries) >= 1
        assert len(keywords) >= 1
        assert "Container shipping regulations" in queries
        assert "logistics" in keywords


class TestDatapointRetrieval:
    """Tests for the datapoint retrieval stage."""
    
    @patch('src.stages.datapoint_retrieval.search_datapoints_for_query')
    @patch('src.stages.datapoint_retrieval.extract_queries_and_keywords')
    def test_retrieve_relevant_datapoints(self, mock_extract, mock_search):
        """Test retrieving relevant datapoints."""
        # Configure the mocks
        mock_extract.return_value = (["query1", "query2"], ["keyword1", "keyword2"])
        mock_search.side_effect = lambda q, c, **kwargs: MOCK_DATAPOINTS if q == "query1" else []
        
        # Prepare test data
        case = {"analysis": MOCK_ANALYSIS}
        
        # Call the function with mocked dependencies
        with patch('src.stages.datapoint_retrieval.get_qdrant_client'):
            result = retrieve_relevant_datapoints(case)
        
        # Validate the result
        assert isinstance(result, dict)
        assert "relevant_datapoints" in result
        assert result["datapoints_complete"] is True
        assert len(result["relevant_datapoints"]) > 0


class TestEnhancement:
    """Tests for the enhancement stage."""
    
    @patch('src.stages.enhancement.find_relevant_guideline')
    @patch('src.stages.enhancement.generate_text')
    def test_enhance_case_with_context(self, mock_generate_text, mock_find_guideline):
        """Test enhancing a case with context."""
        # Configure the mocks
        mock_find_guideline.return_value = {"guideline_type": "test", "content": "Test guideline"}
        mock_generate_text.return_value = "## Case Title\nEnhanced Test Case\n\n## Enhanced Case\nThis is an enhanced case."
        
        # Prepare test case with datapoints
        case = {
            "draft_case": MOCK_DRAFT_CASE["draft_case"],
            "relevant_datapoints": MOCK_DATAPOINTS
        }
        
        # Call the function
        result = enhance_case_with_context(case)
        
        # Validate the result
        assert isinstance(result, dict)
        assert "enhanced_case" in result
        assert "title" in result
        assert result["title"] == "Enhanced Test Case"
        assert mock_generate_text.called


class TestSolution:
    """Tests for the solution development stage."""
    
    @patch('src.stages.solution.generate_text')
    def test_develop_solution(self, mock_generate_text):
        """Test developing a solution for a case."""
        # Configure the mock
        mock_generate_text.return_value = "This is a mock solution to the case."
        
        # Prepare test case
        case = {
            "title": "Test Case",
            "enhanced_case": "This is an enhanced test case.",
            "relevant_datapoints": MOCK_DATAPOINTS
        }
        
        # Call the function
        result = develop_solution(case)
        
        # Validate the result
        assert isinstance(result, dict)
        assert "solution" in result
        assert result["solution_complete"] is True
        assert mock_generate_text.called


if __name__ == "__main__":
    pytest.main(["-v", __file__])