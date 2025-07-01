# Datapoint retrieval stage implementation
"""
Datapoint retrieval stage for maritime logistics case generator.

This module implements the datapoint retrieval stage of the case generation pipeline,
using search queries and keywords from the analysis stage to find relevant 
maritime regulations, requirements, and procedures in the vector database.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from tqdm import tqdm

from ..utils.vector_db import get_qdrant_client, create_embeddings

# Configure logging
logger = logging.getLogger(__name__)

def extract_queries_and_keywords(case: Dict[str, Any]) -> tuple:
    """
    Extract search queries and keywords from the case analysis.
    
    Args:
        case: Dictionary containing the case with analysis
        
    Returns:
        Tuple of (search queries list, keywords list)
    """
    import re
    
    analysis = case.get("analysis", "")
    
    # Try to extract queries
    queries = []
    if "## Search Queries" in analysis:
        queries_section = analysis.split("## Search Queries")[1].split("##")[0]
        for line in queries_section.strip().split("\n"):
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                # Remove leading numbers or bullet points
                clean_line = re.sub(r"^\d+\.\s*|\-\s*", "", clean_line)
                if clean_line:
                    queries.append(clean_line)
    
    # Try to extract keywords
    keywords = []
    if "## Keywords" in analysis:
        keywords_section = analysis.split("## Keywords")[1].split("##")[0] if "##" in analysis.split("## Keywords")[1] else analysis.split("## Keywords")[1]
        for line in keywords_section.strip().split("\n"):
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                # Remove leading numbers or bullet points
                clean_line = re.sub(r"^\d+\.\s*|\-\s*", "", clean_line)
                if clean_line:
                    for word in clean_line.split(","):
                        word = word.strip()
                        if word:
                            keywords.append(word)
    
    # If no queries or keywords found, generate some default ones
    if not queries:
        logger.warning("No search queries found in analysis, using defaults")
        queries = [
            "maritime logistics requirements", 
            "container shipping documentation", 
            "customs clearance procedures",
            "international shipping regulations",
            "port operations standards"
        ]
    
    if not keywords:
        logger.warning("No keywords found in analysis, using defaults")
        keywords = [
            "logistics", 
            "shipping", 
            "maritime", 
            "container", 
            "customs", 
            "documentation", 
            "regulations",
            "compliance"
        ]
    
    # Update the case with extracted queries and keywords
    case["search_queries"] = queries
    case["keywords"] = keywords
    
    logger.info(f"Extracted {len(queries)} queries and {len(keywords)} keywords")
    return queries, keywords

def search_datapoints_for_query(
    query: str, 
    collection_name: str,
    limit: int = 5,
    score_threshold: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Search for datapoints using a single query.
    
    Args:
        query: Search query text
        collection_name: Collection to search in
        limit: Maximum number of results to return per query
        score_threshold: Minimum relevance score threshold
        
    Returns:
        List of datapoint dictionaries with metadata
    """
    client = get_qdrant_client()
    
    # Create embedding
    query_embedding = create_embeddings(query)
    if not query_embedding:
        logger.error(f"Failed to create embedding for query: {query}")
        return []
    
    try:
        # Execute search
        results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False
        )
        
        # Format results
        datapoints = []
        for result in results:
            # Add metadata to the payload
            result.payload["search_score"] = result.score
            result.payload["matched_query"] = query
            result.payload["result_position"] = len(datapoints) + 1
            datapoints.append(result.payload)
        
        logger.info(f"Query '{query}' returned {len(datapoints)} results")
        return datapoints
        
    except Exception as e:
        logger.error(f"Error searching datapoints with query '{query}': {str(e)}")
        return []

def retrieve_relevant_datapoints(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve relevant datapoints using queries and keywords from the case analysis.
    
    Args:
        case: Dictionary containing the case with analysis results
        
    Returns:
        Updated case dictionary with relevant datapoints
    """
    from dotenv import load_dotenv
    import os
    from tqdm import tqdm
    from ..utils.vector_db import search_datapoints
    
    load_dotenv()
    
    # Get collection name from environment or use default
    collection_name = os.getenv("DATAPOINTS_COLLECTION", "logistics_datapoints")  # <-- CHANGE THIS DEFAULT!
    max_points = int(os.getenv("MAX_DATAPOINTS", "30"))
    
    # Extract queries and keywords
    queries, keywords = extract_queries_and_keywords(case)
    logger.info(f"Using {len(queries)} queries and {len(keywords)} keywords to find relevant datapoints")
    
    # Time the data retrieval process
    start_time = datetime.now()
    
    # Retrieve datapoints for each query
    all_datapoints = []
    query_stats = []
    
    # Optional progress bar when running in interactive mode
    query_iterator = tqdm(queries, desc="Retrieving datapoints") if len(queries) > 3 else queries
    
    for query in query_iterator:
        # Search using the query, passing the collection name explicitly
        results = search_datapoints(query, limit=5, collection_name=collection_name)
        
        # Track query performance
        query_stats.append({
            "query": query,
            "results_found": len(results),
            "top_score": results[0].get("search_score", 0) if results else 0
        })
        
        all_datapoints.extend(results)
    
    # Deduplicate datapoints by ID
    unique_datapoints = []
    seen_ids = set()
    
    for datapoint in all_datapoints:
        dp_id = datapoint.get("id", str(hash(str(datapoint))))
        if dp_id not in seen_ids:
            seen_ids.add(dp_id)
            unique_datapoints.append(datapoint)
    
    # Sort by relevance score and limit
    unique_datapoints = sorted(
        unique_datapoints, 
        key=lambda x: x.get("search_score", 0), 
        reverse=True
    )[:max_points]
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log the result
    logger.info(f"Retrieved {len(unique_datapoints)} unique datapoints in {duration:.2f}s")
    
    # Update case with datapoints and metadata
    case.update({
        "relevant_datapoints": unique_datapoints,
        "datapoints_complete": True,
        "stage": "datapoints_retrieved",
        "search_metadata": {
            "collection_name": collection_name,
            "queries_used": len(queries),
            "total_results": len(all_datapoints),
            "unique_datapoints": len(unique_datapoints),
            "retrieval_duration": duration,
            "timestamp": datetime.now().isoformat(),
            "query_stats": query_stats
        }
    })
    
    return case

def get_datapoint_by_id(datapoint_id: str, collection_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve a specific datapoint by its ID.
    
    Args:
        datapoint_id: ID of the datapoint to retrieve
        collection_name: Optional collection name (uses default if not provided)
        
    Returns:
        Datapoint payload or empty dict if not found
    """
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    # Get collection name from environment if not provided
    if not collection_name:
        collection_name = os.getenv("DATAPOINTS_COLLECTION", "logistics_datapoints")  # CHANGED FROM maritime_logistics_kb
    
    client = get_qdrant_client()
    
    try:
        # Retrieve the point
        points = client.retrieve(
            collection_name=collection_name,
            ids=[datapoint_id],
            with_payload=True,
            with_vectors=False
        )
        
        if points:
            return points[0].payload
        else:
            logger.warning(f"Datapoint {datapoint_id} not found in collection {collection_name}")
            return {}
            
    except Exception as e:
        logger.error(f"Error retrieving datapoint {datapoint_id}: {str(e)}")
        return {}

def search_datapoints_by_keywords(
    keywords: List[str], 
    collection_name: Optional[str] = None,
    combine_method: str = "or",
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for datapoints using keywords.
    
    Args:
        keywords: List of keywords to search for
        collection_name: Optional collection name (uses default if not provided)
        combine_method: How to combine keywords ('or' or 'and')
        limit: Maximum number of results to return
        
    Returns:
        List of datapoint payloads matching the keywords
    """
    from dotenv import load_dotenv
    import os
    from qdrant_client.http import models
    
    load_dotenv()
    
    # Get collection name from environment if not provided
    if not collection_name:
        collection_name = os.getenv("DATAPOINTS_COLLECTION", "logistics_datapoints")  # CHANGED FROM maritime_logistics_kb
    
    client = get_qdrant_client()
    
    # Combine keywords using specified method
    if not keywords:
        logger.warning("No keywords provided for search")
        return []
    
    # Create keyword embeddings (using first keyword for vector search direction)
    primary_embedding = create_embeddings(keywords[0])
    if not primary_embedding:
        logger.error(f"Failed to create embedding for keyword: {keywords[0]}")
        return []
    
    try:
        # Create keyword filter
        keyword_conditions = []
        for keyword in keywords:
            # Search for keyword in various payload fields
            keyword_filter = models.Filter(
                should=[
                    models.FieldCondition(
                        key="content",
                        match=models.MatchText(text=keyword)
                    ),
                    models.FieldCondition(
                        key="title",
                        match=models.MatchText(text=keyword)
                    ),
                    models.FieldCondition(
                        key="keywords",
                        match=models.MatchText(text=keyword)
                    )
                ]
            )
            keyword_conditions.append(keyword_filter)
        
        # Combine filters based on method
        if combine_method == "and":
            search_filter = models.Filter(must=keyword_conditions)
        else:  # "or" is the default
            search_filter = models.Filter(should=keyword_conditions)
        
        # Execute search
        results = client.search(
            collection_name=collection_name,
            query_vector=primary_embedding,
            query_filter=search_filter,
            limit=limit,
            with_payload=True
        )
        
        # Extract payloads
        datapoints = []
        for result in results:
            result.payload["search_score"] = result.score
            datapoints.append(result.payload)
        
        logger.info(f"Keyword search with {len(keywords)} keywords returned {len(datapoints)} results")
        return datapoints
        
    except Exception as e:
        logger.error(f"Error searching datapoints by keywords: {str(e)}")
        return []