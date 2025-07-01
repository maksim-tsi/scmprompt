# ADR 004: Case Generation Strategy

## Status
Accepted

## Date
March 28, 2025

## Context
Our maritime logistics knowledge base now contains 1,346 normalized datapoints across multiple ports and entity types. To demonstrate the practical value of this knowledge, we need to generate realistic case studies that:

- Represent authentic logistics scenarios
- Incorporate normalized entities
- Reference relevant regulations and requirements
- Provide educational value for users
- Showcase the capabilities of our vector database

Manual case creation is time-consuming and may not fully leverage our knowledge base. We need an automated approach that maintains quality while scaling efficiently.

## Decision
We will implement a multi-stage case generation pipeline using LLM-based generation combined with vector similarity search:

### Pipeline Stages

┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  1. Initial Draft   │     │  2. Critical Review │     │  3. Enhancement     │     │  4. Solution        │
│  ─────────────────  │     │  ─────────────────  │     │  ─────────────────  │     │  ─────────────────  │
│  • Example-based    │     │  • Guideline-based  │     │  • Domain-specific  │     │  • Evidence-based   │
│  • Context-aware    │ ──> │  • Issue analysis   │ ──> │  • Datapoint-driven │ ──> │  • Regulation-      │
│  • Scenario focused │     │  • Query generation │     │  • Detail enrichment│     │    aligned solution │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘     └─────────────────────┘

1. **Case Draft Generation**
   - Use gemini-2.5-pro-exp-03-25 model (with rate limiting)
   - Seed with randomly selected example case from existing Data/Cases
   - Frame within international container shipping/multimodal logistics context
   - Generate initial case scenario description only

2. **Critical Analysis & Query Generation**
   - Provide model with general Case Generation Guidelines
   - Have model critically evaluate the draft case
   - Generate 10+ search queries and keywords for datapoint retrieval
   - Identify key entities and regulations that should be referenced

3. **Contextual Enhancement**
   - Select most relevant domain-specific guideline (Bishou/Maritime/Ocean Container)
     based on embedding similarity to the case draft
   - Retrieve 10-20 most relevant datapoints from Qdrant using generated queries
   - Provide these resources to the model
   - Have model enhance the case with specific regulatory details and domain accuracy

4. **Solution Development**
   - Generate comprehensive solution referencing specific regulations
   - Allow iterative datapoint retrieval for solution accuracy
   - Format complete case-solution pair in standardized JSON format

### Technical Implementation

- Rate limit API calls (6-second delay between requests)
- Use embedding similarity for guideline selection
- Create dedicated collection for guidelines (sliced by section) in Qdrant
- Maintain traceability between generated cases and source datapoints
- Implement randomization to ensure case diversity

## Alternatives Considered

1. **Purely manual case creation**: Too time-consuming and doesn't fully leverage the datapoints
2. **Simple one-shot generation**: Lacks specificity and regulatory accuracy
3. **Template-based generation**: Too rigid for the diverse logistics scenarios needed

## Consequences

### Positive
- Cases will incorporate accurate regulatory information from our datapoints
- Domain-specific guidelines ensure industry relevance
- Multi-stage approach improves quality over single-pass generation
- Maintains human-in-the-loop option for review and refinement

### Negative
- More complex implementation than simpler approaches
- Dependent on API availability and rate limits
- May require additional embedding storage for guidelines
- Potential for model hallucination requires validation checks

## Implementation Notes

- Implement in a Jupyter notebook (03_Case_Generation.ipynb)
- Store generated cases in Data/GeneratedCases directory
- Log relationships between cases and retrieved datapoints
- Maintain ability to regenerate specific pipeline stages if needed
- Include explicit model instructions to avoid copying example cases