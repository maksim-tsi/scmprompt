# Examples Notebook Guide

## Overview

The `examples.ipynb` notebook demonstrates how to work with generated maritime logistics case examples in the SCM logistics assistant system. This notebook is fundamental to understanding the MedPrompt-inspired approach used throughout the project.

## Purpose

The notebook serves multiple key functions:
1. **Data Exploration**: Load and analyze generated training cases
2. **Quality Assessment**: Evaluate case metrics and qualification status
3. **Case Export**: Export full case studies for detailed review
4. **Prompt Construction**: Demonstrate few-shot learning with real cases
5. **Search Functionality**: Show vector database and fallback search methods

## Recent Enhancements (v0.8.1)

### ✨ New Features
- **Generated Case Integration**: Switched from textbook examples to AI-generated maritime logistics cases
- **Case Export Functionality**: Export complete case studies as formatted text files
- **Quality Metrics Analysis**: Display realism, complexity, and educational value scores
- **Robust Error Handling**: Comprehensive pandas Series and numpy array handling

### 🔧 Technical Improvements
- **Data Source**: Now uses `train_cases.parquet` with 245+ generated cases
- **File Export**: Simplified filename format using case IDs only
- **Search Fallback**: Local text search when vector database unavailable
- **Code Reliability**: Fixed JSON formatting and data type handling issues

## Notebook Structure

### Section 1: Setup and Imports
- Import necessary libraries for data processing and vector search
- Configure paths and environment variables
- Test import functionality

### Section 2: Load Example Data
- Load generated cases from `Data/GeneratedCases/train_cases.parquet`
- Display dataset structure and basic statistics
- Convert data for easier processing

### Section 3: Explore Case Examples
- Analyze case quality metrics across the dataset
- Show qualification status distribution
- Display sample case with full details
- Calculate length statistics for cases and solutions

### Section 3.1: Export Sample Case (New in v0.8.1)
- Export complete case study to text file
- Include all metadata, scenario, solution, and evaluation
- Save to `/Data/GeneratedCases/txt/` directory
- Generate preview and file statistics

### Section 4: Connect to Vector Database
- Test Qdrant connection and configuration
- Display collection information and statistics
- Handle connection errors gracefully

### Section 5: Search for Relevant Examples
- Demonstrate vector-based similarity search
- Show fallback to local text search
- Display search results with quality scores
- Preview matching case content

### Section 6: Example Usage in Prompt Construction
- Format cases for few-shot prompting
- Construct sample prompts with real cases
- Demonstrate MedPrompt approach integration
- Show complete prompt templates

### Section 7: Summary and Next Steps
- Summarize notebook achievements
- Display available data statistics
- Provide guidance for next steps
- Link to related notebooks

## Data Schema

The notebook works with generated cases containing:

```python
{
    'case_id': 'case-20250330-081720-dj177a',
    'title': 'Baltic Salmon Run: Navigating Regulatory Hurdles...',
    'enhanced_case': 'Full case scenario text...',
    'solution': 'Complete solution text...',
    'realism_score': 8.0,
    'complexity_score': 7.0,
    'educational_value': 9.0,
    'solution_quality': 8.0,
    'overall_qualification': 'QUALIFIED',
    'evaluation_summary': 'Case evaluation details...',
    'improvement_suggestions': 'Suggestions for enhancement...'
}
```

## Export Format

Exported text files follow this structure:

```
================================================================================
MARITIME LOGISTICS CASE STUDY
================================================================================

Case ID: case-20250330-081720-dj177a
Title: Baltic Salmon Run: Navigating Regulatory Hurdles...
Exported: 2025-07-19 11:04:12

QUALITY METRICS:
----------------------------------------
Realism Score: 8.0
Complexity Score: 7.0
Educational Value: 9.0
Solution Quality: 8.0
Overall Qualification: QUALIFIED

CASE SCENARIO:
================================================================================
[Full case content...]

SOLUTION:
================================================================================
[Complete solution...]

EVALUATION SUMMARY:
----------------------------------------
[Evaluation details...]
```

## Usage Examples

### Basic Case Loading
```python
# Load cases
examples_df = pd.read_parquet("../Data/GeneratedCases/train_cases.parquet")
print(f"Loaded {len(examples_df)} cases")
```

### Quality Analysis
```python
# Analyze qualified cases
qualified_cases = examples_df[examples_df['overall_qualification'] == 'QUALIFIED']
print(f"Qualified cases: {len(qualified_cases)}")
```

### Case Export
```python
# Export a specific case
case_to_export = examples_df.iloc[0]
# ... export logic handled by notebook
```

### Few-Shot Prompt Construction
```python
# Format case for prompting
formatted_case = format_case_for_prompt(sample_case)
# Use in prompt template...
```

## Best Practices

1. **Environment Setup**: Ensure conda environment 'tsi' is activated
2. **Data Availability**: Verify `train_cases.parquet` exists in the expected location
3. **Vector Database**: Test Qdrant connection before running search examples
4. **Export Directory**: Ensure write permissions for `/Data/GeneratedCases/txt/`
5. **Case Selection**: Use qualified cases for prompt construction when possible

## Troubleshooting

### Common Issues

**Empty DataFrame**: Check parquet file path and permissions
```python
if examples_df.empty:
    print("Check file path: ../Data/GeneratedCases/train_cases.parquet")
```

**Export Errors**: Verify output directory exists and is writable
```python
output_dir.mkdir(parents=True, exist_ok=True)
```

**Vector Search Failures**: Falls back to local search automatically
```python
# Fallback search implemented in notebook
if vector_search_fails:
    use_local_text_search()
```

## Integration with Other Notebooks

- **`02_Test_Queries.ipynb`**: Advanced search building on examples shown here
- **`04_Case_Generation.ipynb`**: Uses case formatting functions from this notebook
- **`08_ICL_Implementation.ipynb`**: Leverages few-shot prompt construction methods
- **`09_Evaluation_ICL_vs_Baseline.ipynb`**: Uses case quality metrics established here

## Future Enhancements

- **Batch Export**: Export multiple cases simultaneously
- **Custom Formatting**: User-defined export templates
- **Advanced Search**: Enhanced filtering and ranking options
- **Quality Visualization**: Charts and graphs for case metrics
- **Case Comparison**: Side-by-side case analysis tools

---

*Last updated: July 19, 2025 (v0.8.1)*
