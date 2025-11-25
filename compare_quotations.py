from pdf_loader import PDFLoader
from llm_extractor import LLMExtractor
from comparison import QuotationComparator
from models import ExtractedQuotation
import json
import pandas as pd
import os

pdf_files = [
    "pdfs/Word_Dummy_quote_filled(Word_variant1)_Guly_Display_AG.pdf",
    "pdfs/Word_Dummy_quote_filled(Word_variant2)_AOE_display_Limited.pdf",
    "pdfs/Word_dummy_quote_filled(Word_Variant4)Futura Components Ltd.pdf",
    "pdfs/Word_dummy_quote_filled(Word_Variant5)_TG_Display_Japan.pdf"
]

print("=" * 60)
print("Quotation Comparison System")
print("=" * 60)

print("\nExtracting quotations from PDFs...")
loader = PDFLoader()
extractor = LLMExtractor(provider="groq", model="llama-3.3-70b-versatile")
quotations = []
extraction_errors = []

for pdf_file in pdf_files:
    print(f"\nProcessing: {pdf_file}")
    try:
        documents = loader.load(pdf_file)
        quotation = extractor.extract(documents)
        quotations.append(quotation)
        print(f"  Extracted: {quotation.supplier_name}")
    except Exception as e:
        error_msg = str(e)
        print(f"  Error: {error_msg[:100]}...")
        extraction_errors.append((pdf_file, error_msg))
        continue

print(f"\n{'='*60}")
print(f"Successfully extracted {len(quotations)} quotation(s) from PDFs")
print(f"{'='*60}")

if len(quotations) < 4 and os.path.exists("results/extracted_quotations.json"):
    print(f"\nLoading missing suppliers from results/extracted_quotations.json...")
    try:
        with open("results/extracted_quotations.json", 'r') as f:
            data = json.load(f)
            existing_names = {q.supplier_name for q in quotations}
            for item in data:
                quote = ExtractedQuotation(**item)
                if quote.supplier_name not in existing_names:
                    quotations.append(quote)
                    print(f"  Loaded: {quote.supplier_name}")
    except Exception as e:
        print(f"  Error loading from JSON: {e}")

if len(quotations) < 4:
    print(f"\nWARNING: Only {len(quotations)}/4 suppliers available")
    if extraction_errors:
        print("Extraction errors occurred (possibly rate limits)")

if quotations:
    os.makedirs("results", exist_ok=True)
    with open("results/extracted_quotations.json", 'w') as f:
        json.dump([q.model_dump() for q in quotations], f, indent=2, default=str)
    print(f"\nSaved {len(quotations)} quotation(s) to: results/extracted_quotations.json\n")

comparator = QuotationComparator()
comparison = comparator.compare(quotations)

print("=" * 80)
print("COMPREHENSIVE COMPARISON TABLE")
print("=" * 80)
df = comparator.to_dataframe(comparison)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)
print(df.to_string(index=False))
print("=" * 80)

print("\n" + "=" * 80)
print("Summary (EUR Normalized + Procurement Scoring):")
if comparison.get("summary"):
    summary = comparison["summary"]
    print(f"  Total Suppliers: {summary.get('total_suppliers', 0)}")
    print(f"  Recommended Supplier: {summary.get('best_supplier', 'N/A')} (Score: {summary.get('best_score', 0):.1f}/100)")
    print(f"  Lowest Cost (EUR): €{summary.get('lowest_cost', 0):,.2f}")
    print(f"  Highest Cost (EUR): €{summary.get('highest_cost', 0):,.2f}")
    print(f"  Cost Range (EUR): €{summary.get('cost_range', 0):,.2f}")
    if comparison.get("comparison_table"):
        top = comparison["comparison_table"][0]
        scores = top.get("scores", {})
        print(f"\n  Recommended Supplier Details ({top['supplier']}):")
        print(f"    Total Score: {top.get('total_score', 0):.1f}/100")
        print(f"    - TCO Score: {scores.get('tco_score', 0):.1f}/100 (35% weight)")
        print(f"    - Delivery Score: {scores.get('delivery_score', 0):.1f}/100 (25% weight)")
        print(f"    - Payment Score: {scores.get('payment_score', 0):.1f}/100 (20% weight)")
        print(f"    Total Cost (EUR): €{top['total_cost_eur']:,.2f}")
        print(f"    Tooling Cost (EUR): €{top['tooling_cost_eur']:,.2f}")
        print(f"    Avg Unit Price (EUR): €{top['unit_cost_avg_eur']:.2f}")
        print(f"    Incoterms: {top['incoterms']}")
        print(f"    Lead Time: {top['lead_time']} ({top.get('lead_time_weeks', 'N/A')} weeks)")
        print(f"    Payment Terms: {top['payment_terms']} ({top.get('payment_days', 'N/A')} days)")
else:
    print("  No quotations to compare")
print("=" * 80)

if comparison.get("recommendation"):
    recommendation = comparison["recommendation"]
    print("\n" + "=" * 80)
    print("RECOMMENDATION WITH REASONING:")
    print("=" * 80)
    print(f"\nRecommended Supplier: {recommendation.get('recommended_supplier', 'N/A')}")
    print(f"Total Score: {recommendation.get('total_score', 0):.1f}/100")
    print(f"\nReasoning:")
    print(f"  {recommendation.get('reasoning', 'N/A')}")
    if recommendation.get("key_advantages"):
        print(f"\nKey Advantages:")
        for advantage in recommendation["key_advantages"]:
            print(f"  - {advantage}")
    if recommendation.get("considerations"):
        print(f"\nConsiderations:")
        for consideration in recommendation["considerations"]:
            print(f"  - {consideration}")
    print("=" * 80)

os.makedirs("results", exist_ok=True)
with open("results/comparison_results.json", 'w') as f:
    json.dump(comparison, f, indent=2, default=str)
comparator.export_to_excel(comparison, "results/comparison_table.xlsx")
print("\nExported: results/comparison_results.json, results/comparison_table.xlsx")
