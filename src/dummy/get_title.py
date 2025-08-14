import re
import os
from PyPDF2 import PdfReader
import openai
from openai import OpenAI
print(os.environ.get('OPENAI_API_KEY'))

client = OpenAI()
def clean_text(text):
    # Loại bỏ tất cả các ký tự không phải chữ cái hoặc số
    cleaned = re.sub(r'^\W+|\W+$', '', text)
    return cleaned

def extract_title_and_subtitle(text):
    """
    Uses a Hugging Face small LLM to extract the main title and subtitle from the document text.
    Returns a tuple: (title, subtitle) or (None, None) if not found.
    """
    
    prompt = (
        "Bạn là một chuyên gia phân tích tài liệu. Ban hãy trích xuất tiêu đề in hoa và chủ đề của tài liệu xuất hiện ngay sau dòng ngày tháng năm từ tài liệu tiếng Việt sau.\n"
        "Hãy trả kết quả về theo format: " +  "\"Tiêu đề_Chủ đề\""
        "Tiêu đề có thể là NGHỊ QUYẾT, TỜ TRÌNH, QUYẾT ĐỊNH, BÁO CÁO, BÁO CÁO THẨM TRA, PHỤ LỤC, THÔNG BÁO, CÔNG VĂN, PHIẾU TRÌNH\n"
        "Chủ đề là nội dung bài viết nằm ngay sau tiêu đề, có thể là một câu hoặc một cụm từ mô tả nội dung chính của tài liệu.\n"
        "\nTài liệu:\n" + text
    )
    print(prompt)
    try:
        response = client.responses.create(
            model="gpt-3.5-turbo",
            input=[
                {"role": "system", "content": "Bạn là một chuyên gia phân tích tài liệu và khắt khe trong công việc. Bạn luôn trả về kết quả theo đúng định dạng được yêu cầu.  "},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        result = response.output_text.strip(r" /.,:\"")
        print("Result:", result)
        if result.strip() == "None":
            return None, None
        return result.split("_", 1) if "_" in result else (result, None)
    except Exception as e:
        print(f"Error during title extraction: {e}")
        return None, None

def extract_title_from_pdf(pdf_path):
    """
    Extracts the document ID from a PDF file by reading its text content.
    Returns the first found document ID, or None if not found.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
        text = reader.pages[0].extract_text()[:500]
        # Uncomment the line below to print the extracted text for debugging
        # print(text)

        return extract_title_and_subtitle(text)
    
    except Exception as e:
        try:
            print(f"Error reading PDF: {e}")
        except Exception:
            print("Error reading PDF and printing error message (possible encoding issue).")
        return None

# Example usage
if __name__ == "__main__":
    pdf_file = r"data\Mẫu phê duyệt tờ trình của KT (đơn giản)\03. 1phiếu trình.pdf"  # Replace with your PDF file path
    title, subtitle = extract_title_from_pdf(pdf_file)
    print(f"Title: {title}\nSubtitle: {subtitle}")
