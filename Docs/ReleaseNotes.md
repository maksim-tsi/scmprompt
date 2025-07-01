# Release Notes - Maritime Logistics Knowledge Base

This document tracks the key changes, improvements, and fixes in each release of our Maritime Logistics Knowledge Base project.

# Release 0.8.0 Planning

## Objectives
- Expand baseline testing with Gemma 3 and similar models
- Implement ICL (In-Context Learning) mechanism for the agent
- Create evaluation framework to compare ICL vs baseline approaches
- Develop a web interface for case solving

## Timeline
- Week 1: Complete baseline testing and analysis
- Week 2: Implement ICL mechanism
- Week 3: Develop evaluation framework and run comparison tests
- Week 4: Build basic web interface prototype

## Implementation Details

### ICL Mechanism
- Retrieve 2-3 most similar cases using vector DB
- Format cases and solutions in prompt
- Implement "reasoning" capability with step-by-step instructions

### Evaluation Framework
- Automatic metrics: Response length, complexity
- LLM-based evaluation: Answer quality, accuracy, specificity
- Human evaluation protocol for small sample

### Web Interface
- Streamlit-based initial prototype
- Case input form
- Interactive response display
- Export functionality

## Dependencies
- Updated requirements.txt with Streamlit and supporting packages

# Previous Project: Magdeburg25 v0.7.0 (Legacy)

## Maritime Logistics Case Generation and Solution Assistant

This release provided a complete implementation of the Magdeburg25 system for maritime logistics case generation and solutions using advanced AI techniques. The current project, scmprompt, is a direct evolution and rebranding of this work.

### Key Features

#### Case Generation Pipeline
- Multi-stage processing with separate analytical phases
- Integration with domain-specific datapoints
- Enhancement with realistic scenarios and challenges

#### In-Context Learning System
- Semantic retrieval of similar cases using embeddings
- Dynamic example selection for improved solutions
- MedPrompt-inspired approach for case solving

#### Vector Database Integration
- Qdrant integration for semantic search
- Efficient storage of cases and solutions

- Pre-populated with 300+ maritime logistics examples

#### Evaluation Framework
- Quality metrics for case realism, complexity, and educational value
- Automated assessment using LLM as judge
- Case filtering based on quality criteria

### Installation

```bash
pip install -r requirements.txt
```

## Version 0.5.0 (March 27, 2025)

### Summary

Our first official release establishes the core infrastructure and data processing pipeline, with a focus on normalized entity representation and vector search capabilities.

### Key Features

- **Entity Name Normalization**: Standardized 500+ entity names down to ~150 canonical forms for improved search consistency
- **Vector Database Integration**: Implemented Qdrant Cloud for persistent, shareable vector storage
- **Datapoint Processing Pipeline**: Established workflow for processing, normalizing, and vectorizing structured data
- **Search Capabilities**: Added semantic search with filtering by port, entity, keywords, and other attributes

### Detailed Changes

#### Data Processing

- Created entity normalization pipeline with mapping dictionary
- Implemented standardized naming conventions for entity types
- Added plurality normalization (e.g., "Shippers" → "Shipper")
- Normalized case inconsistencies (e.g., "CUSTOMER" → "Customer")
- Grouped synonymous terms (e.g., "Client" → "Customer")
- Standardized compound entities (e.g., "Vessels in Narrow Channels" → "Vessel")

#### Infrastructure

- Integrated with Qdrant Cloud for vector storage
- Added UUID conversion for consistent point identification
- Created robust data loading with progress tracking and error handling
- Implemented embedding generation with Google's text-embedding-004

#### Search & Retrieval

- Created utils module for standardized search operations
- Implemented entity filtering with normalized names
- Added multi-filter search capabilities
- Developed Jupyter notebooks for testing and demonstration
- Built rich result display formatting

### Known Issues

- Minor discrepancy between total datapoints loaded (1346) and final collection count (1345) suggests possible duplicate handling
- Search response times may vary due to cloud API latency

### Next Steps

- Implement domain-specific search templates for common use cases
- Add multi-entity relationship exploration
- Improve performance monitoring and analytics
- Develop export functionality for search results