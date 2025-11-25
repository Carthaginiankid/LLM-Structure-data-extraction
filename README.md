# LLM Innovation intern task

## Technical Documentation 


### 1. Overview

This system automates the extraction, normalization, and comparison of supplier quotations to support data-driven procurement decisions. It integrates PDF processing (LlamaIndex), structured LLM-based data extraction, and a quantitative evaluation framework to provide a standardized, repeatable, and auditable supplier assessment workflow.

The solution eliminates manual data entry, reduces comparison errors, and improves sourcing transparency by generating consistent outputs in both JSON and Excel formats.

### 2. Key Capabilities

- Automated extraction from PDFs with heterogeneous layouts
- Multi-currency handling, including automatic normalization to EUR
- Multi-criteria supplier scoring across TCO, Delivery, Payment, Tooling, and MOQ
- LLM-driven recommendation summaries with traceable reasoning
- Professional Excel and JSON outputs suitable for procurement review
- Robust handling of missing information, multilingual terminology, and format inconsistencies

### 3. System Requirements

- Python 3.8 or later (Python 3.11 recommended)
- API credentials for one supported LLM provider (Groq recommended; OpenAI, Anthropic, DeepSeek, Together, Hugging Face, and Ollama are also supported)

### 4. Installation and Setup

#### 4.1 Virtual Environment

Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
```

#### 4.2 Dependencies

Install all required libraries:

```bash
pip install -r requirements.txt
```

This includes LlamaIndex, Instructor, Pydantic, OpenAI client library, Pandas, OpenPyXL, python-dotenv, and other dependencies.

#### 4.3 Environment Configuration

Create a `.env` file in the project root and configure the selected API key:

```bash
GROQ_API_KEY=your_key

# Alternative providers (use only one)
# OPENAI_API_KEY=...
# ANTHROPIC_API_KEY=...
# DEEPSEEK_API_KEY=...
# TOGETHER_API_KEY=...
# HUGGINGFACE_API_KEY=...

# For Ollama (local LLM runtime)
# OLLAMA_BASE_URL=http://localhost:11434/v1
```

#### 4.4 Required Input Files

Place the four supplier quotation PDFs in the project directory:

- `Word_Dummy_quote_filled(Word_variant1)_Guly_Display_AG.pdf`
- `Word_Dummy_quote_filled(Word_variant2)_AOE_display_Limited.pdf`
- `Word_dummy_quote_filled(Word_Variant4)Futura Components Ltd.pdf`
- `Word_dummy_quote_filled(Word_Variant5)_TG_Display_Japan.pdf`

### 5. Execution

#### 5.1 Extraction Process Only

Runs LLM-based extraction across all PDFs:

```bash
python extract_quotation.py
```

**Output:**
- `extracted_quotations.json`

#### 5.2 Full Comparison Workflow

Performs extraction, normalization, scoring, and recommendation generation:

```bash
python compare_quotations.py
```

**Outputs:**
- `comparison_results.json`
- `comparison_table.xlsx` (Supplier Comparison, Recommendation, Summary)

#### 5.3 Selecting an LLM Provider

Change the provider in the extraction or comparison scripts:

```python
extractor = LLMExtractor(provider="groq", model="llama-3.3-70b-versatile")
```

Supported providers: `groq`, `openai`, `anthropic`, `deepseek`, `together`, `huggingface`, `ollama`.

Ollama users must ensure a local model is installed:

```bash
ollama pull llama3.1:8b
```

### 6. Project Structure

```
.
├── pdf_loader.py                 PDF parsing and preprocessing
├── llm_extractor.py              LLM-based structured data extraction
├── models.py                     Pydantic schema definitions
├── comparison.py                 Scoring and recommendation engine
│
├── extract_quotation.py          Extraction workflow
├── compare_quotations.py         Full analysis and comparison workflow
│
├── extracted_quotations.json     Extraction output
├── comparison_results.json       Comparison output
├── comparison_table.xlsx         Excel-based reporting
└── PDF files                     Input quotations
```

### 7. Output Specifications

#### 7.1 Extracted Data (JSON)

`extracted_quotations.json` contains structured, schema-validated fields for each supplier:

- Supplier identity
- Currency and quotation date
- Annual prices and volumes
- Tooling cost breakdowns
- Delivery, payment terms, lead time
- MOQ values

#### 7.2 Comparison Results (JSON)

`comparison_results.json` includes:

- Normalized EUR cost table
- Multi-metric scoring and ranking
- Summary statistics
- LLM-generated recommendation

#### 7.3 Excel Reporting

`comparison_table.xlsx` comprises:

**Supplier Comparison**
Comprehensive dataset including scoring, currency conversions, and procurement conditions.

**Recommendation**
Narrative recommendation paragraph with strengths, considerations, and justification.

**Summary**
High-level analytical overview and scoring methodology.

### 8. System Operation

#### 8.1 PDF Processing

LlamaIndex extracts text and tabular structures from differing PDF templates.

#### 8.2 Data Extraction

LLM extraction constrained by Pydantic schemas via Instructor.

Handles varied terminology, multilingual content, and missing data.

#### 8.3 Scoring and Normalization

All cost values converted to EUR.

TCO calculated per supplier.

Min-Max normalization applied across criteria.

Weighted scoring model applied:

- TCO 35%
- Delivery 25%
- Payment 20%
- Tooling 10%
- MOQ 10%

Missing data penalties included.

#### 8.4 Recommendation Generation

LLM produces unbiased, data-driven recommendations.

Highlights key advantages and trade-off considerations.

### 9. Performance Metrics

- PDF extraction: 2–5 seconds per file
- Scoring and table generation: <1 second
- Recommendation generation: 5–10 seconds
- Full four-file analysis: approximately 10–20 seconds

### 10. Validation Summary

- Verified extraction accuracy across four heterogeneous quotation formats
- Manual validation of TCO calculations and currency conversions
- Correct handling of missing or incomplete fields
- Effective supplier differentiation via scoring framework

### 11. Technical Characteristics

- **Architecture**: PDF Processing → LLM Extraction → Scoring & Recommendation
- **Default model**: Llama 3.3 70B (Groq)
- **Temperature settings**:
  - Extraction: 0.1
  - Recommendation: 0.3
- **Schema validation**: Pydantic
- **Scoring method**: Weighted Min-Max Normalization

### 12. Current Limitations

- OCR not included (non-digital PDFs require pre-processing)
- Uses static currency exchange rates
- Optimized for 4–10 quotations per batch
- Primary language coverage: English and German
- No historical quotation comparison (RAG extension planned)

### 13. Planned Enhancements

- RAG-based historical sourcing comparison
- Real-time exchange rate integration
- OCR support for scanned documents
- Web user interface and REST API
- High-volume batch processing capabilities
