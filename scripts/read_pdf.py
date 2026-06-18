"""从 Chroma 手册 PDF 中提取与网络/IP 连接相关的页面内容，输出到文件。"""
import PyPDF2
import os

pdf_path = r'C:\Users\28468\Desktop\TC_61830_61845_61860_UserManual_202004(1).pdf'
out_path = os.path.join(os.path.dirname(__file__), 'pdf_network_pages.txt')

pdf = PyPDF2.PdfReader(pdf_path)
print(f'Total pages: {len(pdf.pages)}')

keywords = ['ethernet', 'tcp', 'ip address', 'socket', 'network', 'lan',
            'visa', 'scpi', 'remote', 'port', 'gpib', 'usb', 'interface',
            'communication', 'connect']

results = []
for i, page in enumerate(pdf.pages):
    text = page.extract_text() or ''
    lower = text.lower()
    if any(kw in lower for kw in keywords):
        results.append(f'\n{"="*60}\nPage {i+1}\n{"="*60}\n{text[:4000]}\n')

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f'Total pages: {len(pdf.pages)}\n')
    f.write(f'Found {len(results)} pages with network-related keywords\n')
    f.writelines(results)

print(f'Done. Wrote {len(results)} pages to {out_path}')
