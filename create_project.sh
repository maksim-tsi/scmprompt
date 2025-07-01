#!/bin/zsh

# Base directory for the project
BASE_DIR="."

# Function to create a directory if it doesn't exist
create_dir() {
    if [[ ! -d "$1" ]]; then
        mkdir -p "$1"
        echo "Created directory: $1"
    else
        echo "Directory already exists: $1"
    fi
}

# Function to create a file with initial content if it doesn't exist
create_file() {
    local file_path="$1"
    local comment="$2"
    
    if [[ ! -f "$file_path" ]]; then
        echo "# $comment" > "$file_path"
        echo "Created file: $file_path"
    else
        echo "File already exists: $file_path"
    fi
}

# Create base directory
# create_dir "$BASE_DIR"

# Create top-level files
create_file "$BASE_DIR/README.md" "Maritime Case Generator\n\nA modular system for generating maritime logistics case studies."
create_file "$BASE_DIR/requirements.txt" "Required dependencies for the maritime case generator"
create_file "$BASE_DIR/main.py" "Main entry point for the maritime case generator"
create_file "$BASE_DIR/config.py" "Configuration settings for the maritime case generator"

# Create src directory and its structure
create_dir "$BASE_DIR/src"
create_file "$BASE_DIR/src/__init__.py" "Package initialization for maritime case generator"

# Create pipeline directory and files
create_dir "$BASE_DIR/src/pipeline"
create_file "$BASE_DIR/src/pipeline/__init__.py" "Pipeline package initialization"
create_file "$BASE_DIR/src/pipeline/runner.py" "Contains run_case_generation_pipeline function"
create_file "$BASE_DIR/src/pipeline/checkpointing.py" "Checkpoint operations for the pipeline"

# Create stages directory and files
create_dir "$BASE_DIR/src/stages"
create_file "$BASE_DIR/src/stages/__init__.py" "Stages package initialization"
create_file "$BASE_DIR/src/stages/draft_generation.py" "Draft generation stage implementation"
create_file "$BASE_DIR/src/stages/analysis.py" "Analysis stage implementation"
create_file "$BASE_DIR/src/stages/datapoint_retrieval.py" "Datapoint retrieval stage implementation"
create_file "$BASE_DIR/src/stages/enhancement.py" "Contextual enhancement stage implementation"
create_file "$BASE_DIR/src/stages/solution.py" "Solution development stage implementation"

# Create models directory and files
create_dir "$BASE_DIR/src/models"
create_file "$BASE_DIR/src/models/__init__.py" "Models package initialization"
create_file "$BASE_DIR/src/models/case.py" "Case data model implementation"
create_file "$BASE_DIR/src/models/logger.py" "Logging functionality implementation"

# Create utils directory and files
create_dir "$BASE_DIR/src/utils"
create_file "$BASE_DIR/src/utils/__init__.py" "Utils package initialization"
create_file "$BASE_DIR/src/utils/llm.py" "LLM integration utilities"
create_file "$BASE_DIR/src/utils/vector_db.py" "Vector database access utilities"

# Create API directory and files
create_dir "$BASE_DIR/src/api"
create_file "$BASE_DIR/src/api/__init__.py" "API package initialization"
create_file "$BASE_DIR/src/api/endpoints.py" "API endpoints implementation"

# Create tests directory and files
create_dir "$BASE_DIR/tests"
create_file "$BASE_DIR/tests/__init__.py" "Tests package initialization"
create_file "$BASE_DIR/tests/test_pipeline.py" "Tests for the pipeline functionality"
create_file "$BASE_DIR/tests/test_stages.py" "Tests for the pipeline stages"

# Create notebooks directory and files
create_dir "$BASE_DIR/notebooks"
create_file "$BASE_DIR/notebooks/examples.ipynb" "{\"cells\": [], \"metadata\": {\"kernelspec\": {\"display_name\": \"Python 3\", \"language\": \"python\", \"name\": \"python3\"}}, \"nbformat\": 4, \"nbformat_minor\": 5}"

echo "Maritime Case Generator structure has been created!"