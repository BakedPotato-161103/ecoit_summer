from unstructured.documents.elements import Element
from bs4 import BeautifulSoup

def page_processor(elements):
    data = []
    table_elements_coords = [el.metadata.coordinates for el in elements if el.category == "Table"]
    print(table_elements_coords)
    # bboxes1_is_almost_subregion_of_bboxes2
    # Concatenate continual elements
    for el in elements:
        if  len(data) > 0:
            last = data[-1]
            if (el.category[-4:] == "Text" and el.text[0].islower()) and last.category not in ["PageBreak", "Footer", "Table", "Image", "FigureCaption"]:
                data[-1].text += " " + el.text.strip()
                if data[-1].metadata.ocr_text:
                    concat_str = f" {last.metadata.ocr_text}" if last.metadata.ocr_text else ""
                    data[-1].metadata.ocr_text += concat_str
            elif (el.category == "Table" and last.category == "Table"):
                data[-1].metadata.text_as_html += el.metadata.text_as_html
                data[-1].text += " " + el.text.strip()
                if data[-1].metadata.ocr_text:
                    concat_str = f" {last.metadata.ocr_text}" if last.metadata.ocr_text else ""
                    data[-1].metadata.ocr_text += concat_str
            else:
                data.append(el)
            # is_page_break = False
        else:
            data.append(el)
    return data

def html_to_cells(html_text):
    html_table = 