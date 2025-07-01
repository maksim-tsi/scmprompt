# ADR 005: Transition to Modular Architecture for Maritime Case Generator

## Status

Proposed

## Context

Our Maritime Case Generation pipeline is currently implemented as a Jupyter notebook, which has served well for rapid prototyping and experimentation. However, as the system matures, we're encountering several challenges:

- **Code Duplication**: Multiple implementations of the same function exist (e.g., `initialize_checkpoint`, `save_final_case`)
- **State Management**: Notebook execution order impacts functionality, making debugging difficult
- **Maintainability**: Large notebook files are becoming unwieldy to navigate and update
- **Testability**: Testing specific components requires executing entire notebook sections
- **Versioning**: Changes to the system are difficult to track in notebook format
- **Collaboration**: Multiple contributors cannot easily work on different components

The current five-stage pipeline (Draft Generation, Critical Analysis, Datapoint Retrieval, Contextual Enhancement, Solution Development) has proven valuable, but its implementation lacks clear boundaries between components.

## Decision

We will transition from a notebook-based implementation to a modular Python architecture with the following characteristics:

### 1. Component-Based Structure
maritime_case_generator/
├── README.md
├── requirements.txt
├── main.py
├── config.py
├── src/
│   ├── __init__.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── runner.py           # contains run_case_generation_pipeline
│   │   └── checkpointing.py    # checkpoint operations
│   ├── stages/
│   │   ├── __init__.py
│   │   ├── draft_generation.py
│   │   ├── analysis.py
│   │   ├── datapoint_retrieval.py
│   │   ├── enhancement.py
│   │   └── solution.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── case.py             # case data model
│   │   └── logger.py           # logging functionality
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── llm.py              # LLM integration
│   │   └── vector_db.py        # Vector database access
│   └── api/                    # Optional API layer
│       ├── __init__.py
│       └── endpoints.py
├── tests/
│   ├── __init__.py
│   ├── test_pipeline.py
│   └── test_stages.py
└── notebooks/
    └── examples.ipynb          # For demonstrations

### 2. Core Design Principles

- **Single Responsibility**: Each module has a clear, focused purpose
- **Dependency Injection**: Components receive dependencies rather than creating them
- **Configuration Externalization**: All configuration separated from business logic
- **Clear Interfaces**: Well-defined interfaces between components
- **Error Handling**: Consistent error handling throughout the system
- **Logging**: Standardized logging approach across all modules

### 3. Component Interactions

1. **Pipeline Runner**: Orchestrates the overall process flow
2. **Stage Processors**: Each stage is a separate module with defined input/output
3. **Data Models**: Standard representations for cases, datapoints, etc.
4. **External Services**: LLM and vector DB interfaces are abstracted
5. **Utilities**: Shared functionality is centralized

### 4. Key Implementation Decisions

- **Standard Python Modules**: Use Python modules (.py files) instead of notebooks
- **Type Hinting**: Include type hints throughout the codebase
- **Environment Variables**: Use environment variables for sensitive configuration
- **Dependency Management**: Use requirements.txt or Poetry for dependency management
- **Testing Framework**: Implement pytest for automated testing
- **Documentation**: Include docstrings and maintain separate documentation files

## Consequences

### Positive

- **Improved Maintainability**: Clearly separated concerns make code easier to understand
- **Better Collaboration**: Team members can work on different modules simultaneously
- **Enhanced Testability**: Each component can be tested in isolation
- **Simplified Debugging**: Issues can be traced to specific modules
- **Code Reuse**: Functions are defined once and imported where needed
- **Scalability**: System can grow with well-defined boundaries
- **Deployment Options**: Easier to deploy as a service rather than just a notebook
- **Quality**: Supports better code quality practices and tooling

### Challenges

- **Migration Effort**: Converting notebook code to modules requires significant effort
- **Learning Curve**: Team must adapt to the new structure and practices
- **Initial Overhead**: More upfront design work is required
- **Development Speed**: May initially slow down development as structure is established

### Mitigation Strategies

1. **Phased Migration**: Convert one component at a time while maintaining notebook functionality
2. **Comprehensive Testing**: Ensure each migrated component has thorough tests
3. **Documentation**: Document the new architecture and patterns
4. **Template Files**: Create template files for new components
5. **Code Reviews**: Conduct thorough reviews of migrated code

## Implementation Path

1. **Phase 1**: Define core data models and configurations
2. **Phase 2**: Implement utility functions and external service integrations
3. **Phase 3**: Convert each pipeline stage to a separate module
4. **Phase 4**: Create the pipeline runner and checkpointing system
5. **Phase 5**: Implement testing framework and initial tests
6. **Phase 6**: Create documentation and examples
7. **Phase 7**: Optional API/service layer

## Metrics for Success

- Zero duplicate function implementations
- Test coverage > 80%
- Reduced time spent on debugging
- Ability to run individual stages independently
- Successfully generated cases match or exceed quality of notebook-generated cases

## Alternatives Considered

1. **Refactoring Notebooks**: Maintaining notebook structure but improving organization
2. **Microservices**: Full microservices approach with separate services for each stage
3. **Framework-Based**: Using an existing ML pipeline framework

The modular monolith approach was selected as it provides a good balance of separation of concerns and operational simplicity.