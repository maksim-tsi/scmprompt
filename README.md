# LLM Assistant for SCM Logistics Consulting & Problem Solving

## Release Information

For detailed information about features, improvements, and fixes in each version, please see our [Release Notes](./Docs/ReleaseNotes.md).

Current version: 1.0.0 (March 27, 2025)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) <!-- Assuming MIT License -->
[![Status: PoC Phase](https://img.shields.io/badge/Status-PoC%20Phase-orange)]()

This project aims to design, develop, and evaluate an **LLM-powered assistant** providing precise, context-aware decision support, consulting, and problem-solving capabilities within the complex domain of **international multimodal container logistics management**. The core methodology leverages a **MedPrompt-inspired approach**, utilizing detailed case examples for few-shot learning and **Chain-of-Thought (CoT)** reasoning for explainable and structured outputs.

## Motivation

International container logistics is a cornerstone of global trade, yet it faces significant challenges:
*   **Complexity:** Managing multimodal transport chains (sea, rail, road), diverse regulations across ports and countries, and coordinating numerous stakeholders.
*   **Documentation Intensity:** Generating accurate and compliant documentation (Bills of Lading, Customs Declarations, Certificates of Origin, Port Arrival Notices etc.) is critical but often manual, error-prone, and time-consuming.
*   **Decision Support Gaps:** Logistics professionals require timely, context-aware information and reasoning support to navigate disruptions, optimize routes, ensure compliance, and solve emergent problems efficiently.
*   **LLM Potential:** Large Language Models offer powerful capabilities in understanding context, processing information, and generating text, but require significant domain adaptation and grounding in factual knowledge to be reliable in specialized fields like SCM logistics.

This project explores bridging this gap by creating an assistant grounded in specific regulatory knowledge and guided by expert-like reasoning patterns.

## Core Approach & Methodology

Our primary approach is inspired by the **MedPrompt** framework, adapted for the SCM logistics domain. Key elements include:

1.  **Atomic Regulatory Datapoints:** We curate a knowledge base of specific, granular rules and facts ("atomic datapoints") from official port regulations, IMO guidelines, customs rules, etc., stored with rich metadata (e.g., port, category, keywords).
2.  **Rich Case Examples (`scenario_datapoints`):** We generate detailed case examples, each comprising:
    *   A realistic SCM scenario description.
    *   Structured context data (ports, cargo, modes, Incoterms, etc.).
    *   Step-by-step expert reasoning (`expert_analysis_reasoning_steps`) explaining how to determine the required documentation/solution, explicitly referencing relevant atomic regulations.
    *   The ideal output (e.g., `ideal_checklist_items`).
    *   Links to the specific atomic regulations (`relevant_port_regulations`) used.
3.  **Dynamic Few-Shot Learning:** For a new input scenario, the system retrieves the most relevant case examples (using hybrid metadata filtering and semantic search on the atomic datapoints and case contexts).
4.  **Chain-of-Thought (CoT) Prompting:** The retrieved examples and the input scenario are used to construct a prompt that guides the core LLM to "think step-by-step," generating not only the final checklist/solution but also the underlying reasoning trace, grounded in the provided context and learned patterns.
5.  **Fact-Grounded Generation:** The entire process emphasizes grounding the LLM's output in the provided scenario facts and the retrieved regulatory knowledge.

## Key Features / Components (Envisioned)

*   **Scenario Input Interface:** Allows users to describe their logistics scenario.
*   **Atomic Regulation Datastore:** Storage and retrieval mechanism for regulatory facts (PoC: Files + Qdrant Index).
*   **Case Example Datastore:** Storage and retrieval mechanism for rich `scenario_datapoints` (PoC: Files, potentially indexed later).
*   **Literature Datastore:** Processed and embedded knowledge from SCM texts (PoC: Qdrant).
*   **Retrieval Engine:** Implements hybrid metadata/semantic search for regulations and cases.
*   **Case Generation Engine:** LLM-based component to synthesize new `scenario_datapoints` from atomic regulations.
*   **MedPrompt-Inspired Prompting Engine:** Constructs few-shot CoT prompts for the core LLM.
*   **Core LLM:** The underlying Large Language Model (e.g., GPT-4, Gemma-3) performing the reasoning and generation.
*   **Output Generator:** Formats the final checklist/solution and CoT explanation.
*   **Evaluation Module (LLM-as-Judge):** Assesses the quality and accuracy of the assistant's output based on predefined guidelines.
*   **Continuous Learning Pipeline**: Implement automated feedback mechanisms to prioritize case generation for underrepresented or underperforming scenario types

## Current Stage & Roadmap

The project is currently in the **Proof-of-Concept (PoC) Phase**. The primary goal is to demonstrate the feasibility of the core methodology using a sequential workflow implemented via **Jupyter Notebooks**.

**PoC Workflow (Notebook Sequence):**

1.  `01_Data_Ingestion_Regulations.ipynb`: Load/process atomic regulatory JSON datapoints and index them (e.g., into Qdrant) with metadata filtering enabled.
2.  `02_Data_Ingestion_Literature.ipynb`: Parse SCM literature (PDFs), generate embeddings, and load into a separate Qdrant collection.
3.  `03_Case_Generation.ipynb`: Retrieve relevant atomic regulations based on target criteria, prompt the "Case Generation Engine" (LLM) to synthesize rich `scenario_datapoints` (Cases), store generated cases (e.g., as JSON files).
4.  `04_Case_Validation.ipynb`: Implement validation checks (potentially LLM-assisted) on generated cases for plausibility and regulatory consistency. Filter/refine cases.
5.  `05_Assistant_Pipeline.ipynb`: Implement the core MedPrompt-inspired pipeline:
    *   Input a test scenario.
    *   Retrieve relevant few-shot cases (from validated set).
    *   Construct CoT prompt.
    *   Query Core LLM.
    *   Process and display output (checklist + reasoning).
6.  `06_Evaluation.ipynb`: Implement the "LLM-as-Judge" based on defined guidelines (inspired by PST analysis) to evaluate the outputs from Notebook 5 against ground truth evaluation cases. Calculate metrics.
7.  `07_Feedback_Loop.ipynb`: Analyze evaluation results to:
    * Identify scenario types where performance is weaker
    * Generate targeted additional cases for underperforming categories
    * Refine existing cases based on performance patterns
    * Update retrieval strategies (e.g., adjust metadata weights) based on success/failure analysis

**Future Roadmap:**

*   Develop an integrated application (e.g., using Streamlit).
*   Expand the datasets (more regulations, ports, literature, generated cases).
*   Refine retrieval strategies (e.g., graph-based methods, improved embedding techniques).
*   Experiment with different core LLMs.
*   Conduct rigorous quantitative and qualitative evaluations, potentially including user studies.
*   Integrate feedback loops for continuous improvement.

## Technical Stack (PoC Phase)

*   **Language:** Python 3.x
*   **Core Libraries:** Jupyter Notebook, Pandas, Langchain, OpenAI API Client, Sentence Transformers (Hugging Face)
*   **Vector DB:** Qdrant (or similar like Pinecone, Weaviate, FAISS for PoC)
*   **LLMs:** GPT-4 / GPT-3.5-Turbo (via API), potentially open models like Gemma-3 later.
*   **File Formats:** JSON (Atomic Regs, Cases), Markdown/Text (Parsed Literature), PDF
*   **Environment:** Conda / venv, `requirements.txt`

## Preliminary Repository Structure

scmprompt/
├── notebooks/ # Jupyter notebooks for the PoC workflow (01_... to 06_...)
├── data/
│ ├── atomic_regulations/ # Raw JSON files for regulatory datapoints
│ ├── generated_cases/ # Output JSON files for generated scenario_datapoints
│ │ ├── dataset1_fewshot/
│ │ └── dataset2_evaluation/
│ └── literature/ # Raw or processed text/markdown from literature sources
├── src/ # Python source code for reusable functions/classes (Future)
├── docs/ # Project documentation, guidelines, reports
│ ├── guidelines/ # Case Generation & LLM-as-Judge guidelines
│ └── reports/ # Literature review, analysis reports
├── tests/ # Unit tests (Future)
├── .env.example # Example environment file for API keys
├── requirements.txt # Python dependencies
├── LICENSE # Project License file
└── README.md # This file


## Getting Started (PoC Phase)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/maksim-tsi/scmprompt.git
    cd scmprompt
    ```
2.  **Set up Python Environment:**
    ```bash
    # Recommended: Create and activate a virtual environment (e.g., conda or venv)
    # conda create -n mscmprompt python=3.10
    # conda activate scmprompt
    pip install -r requirements.txt
    ```
3.  **Configure API Keys:**
    *   Copy `.env.example` to `.env`.
    *   Fill in your `OPENAI_API_KEY` and any other necessary credentials (e.g., Qdrant API key/URL if using cloud).
4.  **Prepare Data:**
    *   Place raw atomic regulation JSON files in `data/atomic_regulations/`.
    *   Place literature PDF files in `data/literature/` (or configure paths in Notebook 2).
5.  **Run Notebooks:** Execute the notebooks in numerical order (`01_...` through `06_...`) within the `notebooks/` directory. Each notebook typically loads data from previous steps (or raw sources) and saves its output for the next step. Follow instructions within each notebook.

## Data

The project utilizes three main categories of data:

1.  **Atomic Regulatory Datapoints:** Structured JSON objects detailing specific rules from international (IMO) and port-specific (e.g., Riga, Singapore, Shanghai) regulations. Stored initially as files, indexed in Qdrant for retrieval.
2.  **SCM Literature:** Textual knowledge extracted from relevant books, research papers, and industry reports. Processed into text chunks, embedded, and stored in Qdrant.
3.  **Case Scenarios (`scenario_datapoints`):** Rich JSON objects generated by the "Case Generation Engine" (Notebook 3), containing descriptions, context, reasoning, checklists, and regulatory links. Used for few-shot learning and evaluation. Stored as files in `data/generated_cases/`.

*(Note: Ensure compliance with data usage rights and licenses for all external data sources.)*

## Evaluation

The primary evaluation (Notebook 6) uses an "LLM-as-Judge" approach, guided by principles derived from McKinsey PST analysis. Key evaluation criteria include:

*   **Checklist Accuracy:** Precision, Recall, F1-score compared to `ideal_checklist_items`.
*   **Reasoning Quality:** Assessed on:
    *   Scenario Interpretation Accuracy
    *   Factual Grounding & Data Handling
    *   Logical Soundness & Validity
    *   Explanatory Quality & Causality
    *   Structure & Clarity

## Contributing

This is currently a research project. Contributions are welcome in the future. Please refer to `CONTRIBUTING.md` (to be created) or open an issue to discuss potential contributions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

*   Maksim Ilin, TSI - ilin.m@tsi.lv
*   Open an issue on this GitHub repository for technical questions or bug reports.

*(Please cite this repository/associated publication if using concepts or code from this project.)*

## Environment Variables & Credentials

This project uses environment variables to securely manage all credentials and API keys. **Do not hardcode any credentials in code or notebooks.**

### Required Environment Variables

- `GOOGLE_API_KEY`: API key for Google Generative AI (required for embedding and LLM calls)
- `QDRANT_URL`: URL for your Qdrant Cloud instance
- `QDRANT_API_KEY`: API key for Qdrant Cloud
- `OPENAI_API_KEY`: (if using OpenAI models)
- Any other service-specific keys (see relevant code or .env.example)

**How to set up:**
1. Copy `.env.example` to `.env` in the project root.
2. Fill in all required variables with your own credentials.
3. Never commit your `.env` file or any credentials to version control.

All code and notebooks are designed to load credentials from environment variables using the `python-dotenv` package. If a required variable is missing, the code will raise an error and prompt you to set it.