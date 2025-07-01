# ADR 001: Vector Database Selection for PoC Phase

## Status
Updated (2025-03-27) - Original decision reconsidered due to multi-environment development needs

## Context
The project requires storage and retrieval of:
- ~1000+ atomic regulatory datapoints with metadata filtering
- Embedding-based semantic search capabilities
- Simplified development in a notebook environment

**Additional context:**
- Development will occur across multiple environments (local, Google IDX cloud IDE, GitHub Codespaces)
- Need for consistent data access across all environments

## Decision
We will use Qdrant Cloud (Free tier) instead of local ChromaDB for the PoC phase.

## Rationale
1. **Multi-environment consistency**: Qdrant Cloud provides consistent access from any development environment
2. **No synchronization needed**: Eliminates the need to sync database files between environments
3. **Persistence between sessions**: Data remains available regardless of which environment is used
4. **Reduced local resource usage**: Cloud-hosted option saves local computing resources
5. Still provides necessary hybrid search capabilities (metadata + vector)
6. Free tier sufficient for PoC scale (~1000 documents)

## Consequences
- Positive: Consistent experience across all development environments
- Positive: No need to manage/commit large binary database files to Git
- Positive: Easier collaboration with potential team members
- Negative: Adds external dependency on Qdrant Cloud service
- Negative: Requires internet connection for development
- Negative: Potential minor latency increase compared to local solution

## Alternatives Considered
- Local ChromaDB with persistence: Problematic for syncing across environments
- ChromaDB files in Git repository: Would create issues with large binary files in Git
- Simple pandas + numpy approach: Too limited for hybrid search requirements

## Implementation Notes
- Create a shared Qdrant Cloud instance for the project
- Store connection details securely (not in the repository)
- Document setup process for new developers joining the project
- Consider local fallback options for offline development if needed