"""
Qdrant Cloud utilities for the scmprompt project.
Provides standardized access to Qdrant collections for logistics datapoints.
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Collection name constant
COLLECTION_NAME = "logistics_datapoints"

def get_qdrant_client():
    """
    Returns a configured Qdrant client using environment variables.
    """
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        raise EnvironmentError("Missing QDRANT_URL or QDRANT_API_KEY environment variables")
        
    return QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key
    )

def get_embedding(text):
    """
    Generate embeddings using Google's text-embedding-004 model.
    
    Args:
        text (str): Text to generate embedding for
        
    Returns:
        list: Vector embedding or None if generation failed
    """
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError("Missing GOOGLE_API_KEY environment variable")
    
    try:
        embedding_response = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        
        return embedding_response["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def search_datapoints(query, filter_conditions=None, limit=5, collection_name=COLLECTION_NAME):
    """
    Search for datapoints using semantic search with optional filters.
    
    Args:
        query (str): The search query
        filter_conditions (dict, optional): Dictionary of field:value pairs for filtering
        limit (int, optional): Maximum number of results to return
        collection_name (str, optional): Name of the Qdrant collection
        
    Returns:
        list: Search results with payloads and scores
    """
    # Get client
    client = get_qdrant_client()
    
    # Generate embedding for query
    query_embedding = get_embedding(query)
    if query_embedding is None:
        raise ValueError("Failed to generate embedding for query")
    
    # Build search filter
    search_filter = None
    if filter_conditions:
        must_conditions = []
        
        for field, value in filter_conditions.items():
            if field == "keywords":
                if isinstance(value, list):
                    must_conditions.append(
                        models.FieldCondition(
                            key=field,
                            match=models.MatchAny(any=value)
                        )
                    )
                else:
                    must_conditions.append(
                        models.FieldCondition(
                            key=field,
                            match=models.MatchValue(value=value)
                        )
                    )
            else:
                must_conditions.append(
                    models.FieldCondition(
                        key=field,
                        match=models.MatchValue(value=value)
                    )
                )
                
        search_filter = models.Filter(must=must_conditions)
    
    # Execute search
    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=limit
    )
    
    return results

def create_collection(collection_name=COLLECTION_NAME, recreate=False):
    """
    Create a new collection for logistics datapoints.
    
    Args:
        collection_name (str): Name for the collection
        recreate (bool): Whether to recreate the collection if it already exists
        
    Returns:
        bool: True if collection was created/exists, False otherwise
    """
    client = get_qdrant_client()
    
    # Check if collection exists
    collections = client.get_collections().collections
    if any(c.name == collection_name for c in collections):
        if not recreate:
            print(f"Collection '{collection_name}' already exists")
            return True
        else:
            client.delete_collection(collection_name)
            print(f"Deleted existing collection '{collection_name}'")
    
    # Create collection with Google's embedding dimension (768)
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=768,  # Google text-embedding-004 dimension
            distance=models.Distance.COSINE
        ),
        on_disk_payload=True,  # Store payload on disk for larger datasets
    )
    print(f"Created collection '{collection_name}'")
    
    # Create indices for efficient filtering
    index_fields = [
        "datapoint_id", 
        "datapoint_type", 
        "port_area", 
        "domain_area",
        "relevant_entity", 
        "regulation_category", 
        "regulation_subcategory", 
        "document_type",
        "source_document",
        "keywords"
    ]
    
    for field in index_fields:
        if field == "keywords":
            # Keywords is an array field
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
                is_filterable=True
            )
        else:
            # Other fields are keyword fields
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
                is_filterable=True
            )
            
    print(f"Created indices for fields: {', '.join(index_fields)}")
    return True

def test_connection(collection_name=COLLECTION_NAME):
    """
    Test connection to Qdrant Cloud and optionally a specific collection.
    
    Args:
        collection_name (str, optional): Name of collection to check
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections
        print(f"✅ Successfully connected to Qdrant Cloud.")
        print(f"Available collections: {[c.name for c in collections]}")
        
        # Test Google API connection
        test_embedding = get_embedding("Test embedding generation")
        print(f"✅ Successfully connected to Google Embedding API.")
        print(f"Embedding dimension: {len(test_embedding)}")
        
        # Test specific collection if provided
        if collection_name:
            if any(c.name == collection_name for c in collections):
                collection_info = client.get_collection(collection_name)
                print(f"✅ Collection '{collection_name}' exists with {collection_info.vectors_count} points")
                return True
            else:
                print(f"❌ Collection '{collection_name}' does not exist")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def get_collection_stats(collection_name=COLLECTION_NAME):
    """
    Get statistics about a collection.
    
    Args:
        collection_name (str): Name of the collection
        
    Returns:
        dict: Collection statistics
    """
    client = get_qdrant_client()
    
    try:
        # Get basic collection info
        collection_info = client.get_collection(collection_name)
        
        # Get datapoint type counts
        datapoint_types = {}
        port_areas = {}
        entities = {}
        
        # Use scroll to get all points
        points, _ = client.scroll(
            collection_name=collection_name,
            limit=10000,  # Adjust based on your collection size
            with_payload=True,
            with_vectors=False
        )
        
        for point in points:
            # Count datapoint types
            datapoint_type = point.payload.get("datapoint_type")
            if datapoint_type:
                datapoint_types[datapoint_type] = datapoint_types.get(datapoint_type, 0) + 1
            
            # Count port areas
            port_area = point.payload.get("port_area")
            if port_area:
                port_areas[port_area] = port_areas.get(port_area, 0) + 1
                
            # Count entities
            entity = point.payload.get("relevant_entity")
            if entity:
                entities[entity] = entities.get(entity, 0) + 1
        
        return {
            "name": collection_name,
            "vectors_count": collection_info.vectors_count,
            "indexed_vectors": collection_info.indexed_vectors,
            "status": collection_info.status,
            "datapoint_types": datapoint_types,
            "port_areas": port_areas,
            "entities": entities
        }
    except Exception as e:
        print(f"Error getting collection statistics: {e}")
        return None