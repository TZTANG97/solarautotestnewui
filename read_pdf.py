from pypdf import PdfReader

pdf_path = r'C:\Users\28468\Desktop\workspace\命令文档\德威创命令汉化整理\DEWETRON_Oxygen_SCPI_Technical_Reference_V1.16.pdf'
output_path = r'C:\Users\28468\Desktop\workspace\codes\solarautotestdev\dewetron_scpi_docs.txt'

reader = PdfReader(pdf_path)
print(f'Total pages: {len(reader.pages)}')

with open(output_path, 'w', encoding='utf-8') as out:
    out.write(f'Total pages: {len(reader.pages)}\n')
    for i in range(min(40, len(reader.pages))):
        text = reader.pages[i].extract_text()
        if text:
            out.write(f'--- Page {i+1} ---\n')
            out.write(text)
            out.write('\n\n')

print(f'Done. Saved to {output_path}')
