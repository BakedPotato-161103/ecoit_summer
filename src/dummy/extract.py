
import re
import os
from PyPDF2 import PdfReader

def extract_document_id(text):
    """
    Extracts the document ID from the given text.
    The ID format is: {number}/{Type}-{Owner} or {number}/{Owner}
    Example: 8495/QĐ-EVNHANOI or 8495/QĐ
    Returns the first match found, or None if not found.
    """
    # Pattern: number/word(-word)?
    pattern = r"\b(\d+)/(\w+)(?:-(\w+))?\b"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None

def extract_id_from_pdf(pdf_path):
    """
    Extracts the document ID from a PDF file by reading its text content.
    Returns the first found document ID, or None if not found.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return extract_document_id(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

# Example usage
if __name__ == "__main__":
    import hydra
    from omegaconf import DictConfig
    import os
    import rootutils
    rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

    print(os.getcwd())

    samples = [
        "Quyết định số 07/KT ban hành ngày...",
        "Văn bản 1234/KT trình bày...",
        "Không có mã nào ở đây.",
        "Số 5678/ABC-XYZ được duyệt."  
    ]
    for s in samples:
        print(f"Input: {s}\nExtracted ID: {extract_document_id(s)}\n")
    
    with hydra.initialize(version_base='1.3', config_path="../../config", job_name="create_table"):
        cfg= hydra.compose(config_name="app.yaml")
    # Example for PDF extraction
    print(cfg.paths.data_dir)
    pdf_file = cfg.paths.data_dir +  r"/Mẫu phê duyệt tờ trình của KT (đơn giản)/03. Báo cáo thẩm tra.pdf"
    print(f"Extracted ID from PDF: {extract_id_from_pdf(pdf_file)}")
