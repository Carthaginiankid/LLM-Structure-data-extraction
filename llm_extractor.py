import os
from typing import Optional
from openai import OpenAI
import instructor
from llama_index.core import Document
from dotenv import load_dotenv
from models import ExtractedQuotation

load_dotenv()


class LLMExtractor:
    def __init__(self, provider: str = "groq", model: str = "llama-3.3-70b-versatile", api_key: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model
        
        if self.provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            api_key = "ollama"
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.client = instructor.patch(self.client)
            if not model or model == "llama-3.3-70b-versatile":
                self.model = "llama3.1:8b"
        elif self.provider == "groq":
            api_key = api_key or os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("Groq API key required. Set GROQ_API_KEY env var or pass api_key")
            base_url = "https://api.groq.com/openai/v1"
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.client = instructor.patch(self.client)
        elif self.provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key")
            self.client = OpenAI(api_key=api_key)
            self.client = instructor.patch(self.client)
        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                import instructor as instructor_lib
                api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var or pass api_key")
                anthropic_client = Anthropic(api_key=api_key)
                self.client = instructor_lib.from_anthropic(anthropic_client)
                if not model or model == "llama-3.3-70b-versatile":
                    self.model = "claude-3-5-sonnet-20241022"
            except ImportError:
                raise ImportError("anthropic package required. Install: pip install anthropic instructor-anthropic")
        elif self.provider == "deepseek":
            api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DeepSeek API key required. Set DEEPSEEK_API_KEY env var or pass api_key")
            base_url = "https://api.deepseek.com/v1"
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.client = instructor.patch(self.client)
            if not model or model == "llama-3.3-70b-versatile":
                self.model = "deepseek-chat"
        elif self.provider == "together":
            api_key = api_key or os.getenv("TOGETHER_API_KEY")
            if not api_key:
                raise ValueError("Together AI API key required. Set TOGETHER_API_KEY env var or pass api_key")
            base_url = "https://api.together.xyz/v1"
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.client = instructor.patch(self.client)
            if not model or model == "llama-3.3-70b-versatile":
                self.model = "meta-llama/Llama-3-70b-chat-hf"
        elif self.provider == "huggingface":
            api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                raise ValueError("Hugging Face API key required. Set HUGGINGFACE_API_KEY env var or pass api_key")
            base_url = "https://api-inference.huggingface.co/v1"
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.client = instructor.patch(self.client)
            if not model or model == "llama-3.3-70b-versatile":
                self.model = "meta-llama/Llama-3-8b-chat-hf"
        elif self.provider == "openrouter":
            api_key = api_key or os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY env var or pass api_key")
            base_url = "https://openrouter.ai/api/v1"
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.client = instructor.patch(self.client)
            if not model or model == "llama-3.3-70b-versatile":
                self.model = "meta-llama/llama-3.1-70b-instruct"
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported: ollama, groq, openai, anthropic, deepseek, together, huggingface, openrouter")

    def extract(self, documents: list[Document]) -> ExtractedQuotation:
        text = "\n\n--- Page Separator ---\n\n".join([doc.text for doc in documents])
        quotation = self.client.chat.completions.create(
            model=self.model,
            response_model=ExtractedQuotation,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Extract structured data from this quotation:\n\n{text}"}
            ],
            temperature=0.1
        )
        return quotation

    def _get_system_prompt(self) -> str:
        return """You are an expert procurement analyst extracting structured data from supplier quotations.

Handle ALL variations:

1. DATE FORMATS (normalize to ISO: YYYY-MM-DD):
   - "21-Oct-2025" → 2025-10-21
   - "21.10.2025" → 2025-10-21
   - "21/10/2025" → 2025-10-21

2. FIELD LABEL VARIATIONS:
   - Annual Quantity: "Volume", "Annual Quantity", "Annual Peak Volume", "Yearly Quantity"
   - Tooling Cost: "Tooling Cost", "NRE", "Development Cost", "Tooling Fee"
   - Tooling Renewal Cost: "Tooling renewal cost", "Annual Tooling", "Recurring Tooling" - If "renewal" or "recurring", set tooling_cost_type to "renewal" and extract annual amount (multiplied by years).
   - Delivery Terms: "Delivery Terms", "Delivery Condition", "Incoterms", "Delivery Terms for Part"

3. NUMBER FORMATS:
   - European: "50.000" → 50000 (dots as thousand separators)
   - US: "50,000" → 50000 (commas as thousand separators)
   - Prices: "37.00" → 37.00 (decimal point)

4. CURRENCY VARIATIONS:
   - Detect from symbols (€, $, £, ¥) and codes (EUR, USD, GBP, JPY)
   - Normalize to ISO codes

5. MULTI-LANGUAGE:
   - German: "Wochen" = weeks, "Anzahlung" = down payment
   - Translate to English equivalents

6. MISSING FIELDS:
   - If field is missing, use null/None
   - If placeholder like "<Validity>", treat as missing

7. TABLE EXTRACTION:
   - Extract prices and quantities from tables
   - Map years to prices and quantities correctly
   - IMPORTANT: annual_prices and annual_quantities must use ACTUAL YEAR NUMBERS (e.g., 2027, 2028, 2029)
   - Do NOT use "Year 1", "Year 2" - extract the actual calendar year from the PDF
   - If year is not specified, infer from quotation date or use sequential years starting from current year

Extract data exactly matching the provided Pydantic schema."""
