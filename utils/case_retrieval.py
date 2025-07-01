# Utilities for retrieving similar case examples for in-context learning.
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.qdrant_client import get_qdrant_client, get_embedding

def retrieve_similar_cases(new_case_text, num_examples=2, collection_name="icl_logistics_case_examples"):
    """Retrieve similar cases for in-context learning.
    
    Args:
        new_case_text: The new case text
        num_examples: Number of examples to retrieve
        collection_name: Name of the Qdrant collection with case examples
            
    Returns:
        List of example cases with their solutions
    """
    
    # Get client
    client = get_qdrant_client()
    
    # Generate embedding for new case
    new_case_embedding = get_embedding(new_case_text)
    
    if not new_case_embedding:
        print("⚠️ Failed to generate embedding for the case")
        return []
    
    # Search for similar cases
    similar_cases = client.search(
        collection_name=collection_name,
        query_vector=new_case_embedding,
        limit=num_examples
    )
    
    # Format the results
    examples = []
    for result in similar_cases:
        example = {
            "title": result.payload["title"],
            "case_id": result.payload["case_id"],
            "solution": result.payload["solution"],
            "similarity_score": result.score
        }
        examples.append(example)
    
    return examples