from pdf_loader import PDFLoader
from llm_extractor import LLMExtractor
import json

pdf_files = [
    "Word_Dummy_quote_filled(Word_variant1)_Guly_Display_AG.pdf",
    "Word_Dummy_quote_filled(Word_variant2)_AOE_display_Limited.pdf",
    "Word_dummy_quote_filled(Word_Variant4)Futura Components Ltd.pdf",
    "Word_dummy_quote_filled(Word_Variant5)_TG_Display_Japan.pdf"
]

print("=" * 60)
print("PDF Quotation Extraction - All PDFs")
print("=" * 60)

loader = PDFLoader()
extractor = LLMExtractor(provider="groq", model="llama-3.3-70b-versatile")
all_quotations = []

for pdf_file in pdf_files:
    print(f"\n{'='*60}")
    print(f"Processing: {pdf_file}")
    print(f"{'='*60}")
    
    try:
        documents = loader.load(pdf_file)
        quotation = extractor.extract(documents)
        all_quotations.append(quotation)

        print("\nExtracted Data:")
        print("-" * 60)
        print(f"Supplier: {quotation.supplier_name}")
        print(f"Currency: {quotation.currency.value}")
        if quotation.annual_prices:
            print(f"\nAnnual Prices:")
            for year in sorted(quotation.annual_prices.keys()):
                print(f"  {year}: {quotation.annual_prices[year]} {quotation.currency.value}")
        if quotation.annual_quantities:
            print(f"\nAnnual Quantities:")
            for year in sorted(quotation.annual_quantities.keys()):
                print(f"  {year}: {quotation.annual_quantities[year]:,} units")
        if quotation.tooling_cost:
            print(f"\nTooling Cost: {quotation.tooling_cost} {quotation.currency.value}")
            if quotation.tooling_cost_type:
                print(f"Tooling Cost Type: {quotation.tooling_cost_type}")
        if quotation.delivery_terms:
            print(f"\nDelivery Terms: {quotation.delivery_terms}")
        if quotation.payment_terms:
            print(f"Payment Terms: {quotation.payment_terms}")
        if quotation.lead_time:
            print(f"Lead Time: {quotation.lead_time}")
        if quotation.moq:
            print(f"MOQ: {quotation.moq:,}")
        if quotation.quotation_date:
            print(f"\nQuotation Date: {quotation.quotation_date.strftime('%Y-%m-%d')}")
        print("-" * 60)
        
    except Exception as e:
        print(f"   Error processing {pdf_file}: {e}")
        continue

print(f"\n{'='*60}")
print(f"Summary: Successfully extracted {len(all_quotations)} quotation(s)")
print(f"{'='*60}")

output_file = "extracted_quotations.json"
with open(output_file, 'w') as f:
    json.dump([q.model_dump() for q in all_quotations], f, indent=2, default=str)
print(f"Saved to: {output_file}")
