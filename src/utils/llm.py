# LLM integration utilities
"""
LLM interaction utilities for the Maritime Case Generator.

This module provides standardized functions for interacting with language models,
including text generation, prompt formatting, and response handling.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

# Add at the top of the file
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))  # Add project root to path
import config  # Ensure Google API is configured

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError(
        "Required package not installed. Please run: "
        "pip install google-generativeai"
    )

# Configure logging
logger = logging.getLogger(__name__)

def initialize_llm(model_name: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """
    Initialize the language model client.
    
    Args:
        model_name: Name of the model to use (defaults to config value)
        api_key: API key for accessing the model (defaults to environment variable)
    
    Returns:
        The name of the initialized model
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    # Use provided API key or get from environment
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("No API key provided. Set GOOGLE_API_KEY environment variable or pass as parameter.")
    
    # Configure the Google Generative AI client
    genai.configure(api_key=api_key)
    
    # Use provided model name or get from environment
    model_name = model_name or os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
    
    logger.info(f"Initialized LLM: {model_name}")
    return model_name

def generate_text(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: float = 0.95,
    top_k: int = 40,
    stop_sequences: Optional[List[str]] = None,
    retry_count: int = 2,
    retry_delay: int = 5
) -> str:
    """
    Generate text using the configured language model.
    
    Args:
        prompt: Text prompt to generate from
        model: Model name (if None, uses the default from initialize_llm)
        temperature: Sampling temperature (higher = more creative, lower = more deterministic)
        max_tokens: Maximum number of tokens to generate (None = model default)
        top_p: Nucleus sampling parameter
        top_k: Top-k sampling parameter
        stop_sequences: List of sequences that will stop generation when encountered
        retry_count: Number of retries if generation fails
        retry_delay: Delay in seconds between retries
    
    Returns:
        Generated text string
    
    Raises:
        RuntimeError: If text generation fails after all retries
    """
    # Initialize model if not done already
    if not model:
        model = initialize_llm()
    
    # Create generation config
    generation_config = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
    }
    
    if max_tokens:
        generation_config["max_output_tokens"] = max_tokens
        
    if stop_sequences:
        generation_config["stop_sequences"] = stop_sequences
    
    # Create the model instance
    genai_model = genai.GenerativeModel(model_name=model)
    
    # Track timing
    start_time = datetime.now()
    
    # Try generation with retries
    last_error = None
    for attempt in range(retry_count + 1):
        try:
            logger.info(f"Generating text with {model}, temperature={temperature}")
            
            response = genai_model.generate_content(
                contents=prompt,
                generation_config=genai.GenerationConfig(**generation_config)
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Extract the response text
            if hasattr(response, 'text'):
                generated_text = response.text
            elif hasattr(response, 'parts') and response.parts:
                generated_text = response.parts[0].text
            else:
                # Try to extract from candidates if present
                if hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0], 'content'):
                    generated_text = response.candidates[0].content.parts[0].text
                else:
                    logger.error(f"Unexpected response structure: {type(response)}")
                    generated_text = str(response)
            
            # Log the result
            logger.info(f"Generated {len(generated_text)} chars in {duration:.2f}s")
            return generated_text
            
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Generation attempt {attempt+1}/{retry_count+1} failed: {last_error}")
            
            if attempt < retry_count:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    # If we get here, all attempts failed
    error_msg = f"Text generation failed after {retry_count + 1} attempts: {last_error}"
    logger.error(error_msg)
    raise RuntimeError(error_msg)

def format_prompt(template: str, **kwargs) -> str:
    """
    Format a prompt template with provided variables.
    
    Args:
        template: The prompt template string with {variable} placeholders
        **kwargs: Variables to substitute in the template
    
    Returns:
        Formatted prompt string
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Missing variable in prompt template: {e}")
        raise ValueError(f"Missing variable in prompt template: {e}")

def list_available_models() -> List[Dict[str, Any]]:
    """
    List available models that can be used with the LLM client.
    
    Returns:
        List of model information dictionaries
    """
    try:
        # Initialize if needed
        initialize_llm()
        
        # Get available models
        models = genai.list_models()
        return [
            {
                "name": model.name,
                "display_name": model.display_name,
                "description": model.description,
                "supported_generation_methods": model.supported_generation_methods
            }
            for model in models
            if "generateContent" in model.supported_generation_methods
        ]
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return []

def test_llm_connection(model: Optional[str] = None) -> Dict[str, Any]:
    """
    Test the connection to the LLM provider.
    
    Args:
        model: Optional specific model to test
        
    Returns:
        Dictionary with test results including success status and timing
    """
    try:
        start_time = time.time()
        model_name = initialize_llm(model)
        
        # Simple test prompt
        prompt = "Generate a one-sentence description of maritime logistics."
        
        # Generate text
        result = generate_text(prompt, model=model_name, temperature=0.1, max_tokens=50)
        
        duration = time.time() - start_time
        
        return {
            "success": True,
            "model": model_name,
            "response_length": len(result),
            "duration_seconds": duration,
            "sample_output": result[:100] + ("..." if len(result) > 100 else ""),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"LLM connection test failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Set up console logging
    logging.basicConfig(level=logging.INFO)
    
    # Simple test when module is run directly
    print("Testing LLM connection...")
    result = test_llm_connection()
    
    if result["success"]:
        print(f"✅ LLM connection successful!")
        print(f"Model: {result['model']}")
        print(f"Response time: {result['duration_seconds']:.2f}s")
        print(f"Sample output: {result['sample_output']}")
    else:
        print(f"❌ LLM connection failed: {result['error']}")