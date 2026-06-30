import fitz  # PyMuPDF

pdf_path = "Doc1.pdf"  # change filename

doc = fitz.open(pdf_path)

print("Total Pages:", len(doc))

all_text = ""

for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    all_text += text

print("\n--- Extracted Text Preview ---\n")
print(all_text[:1000])  # first 1000 chars

print("\nTotal Characters Extracted:", len(all_text))