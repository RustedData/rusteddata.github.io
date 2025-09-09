from PyPDF2 import PdfReader, PdfWriter

pdf1_path = "C:/Users/bakke/OneDrive/Documents/rusteddata.github.io/qrcards_text_side.pdf"
pdf2_path = "C:/Users/bakke/OneDrive/Documents/rusteddata.github.io/qrcards_with_bg.pdf"
output_path = "C:/Users/bakke/OneDrive/Documents/rusteddata.github.io/qrcards_combined.pdf"

reader1 = PdfReader(pdf1_path)
reader2 = PdfReader(pdf2_path)
writer = PdfWriter()

num_pages = max(len(reader1.pages), len(reader2.pages))

for i in range(num_pages):
    if i < len(reader1.pages):
        writer.add_page(reader1.pages[i])
    if i < len(reader2.pages):
        writer.add_page(reader2.pages[i])

with open(output_path, "wb") as f:
    writer.write(f)

print(f"Combined PDF written to {output_path}")
