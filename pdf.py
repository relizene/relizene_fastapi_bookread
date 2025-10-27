import fitz
import base64
import io
import re


def pdf_formater(book_content, book_name, book_id):
    """Берет данные закодированные в base 64, затем сохраняет его в пдф файл и с помощью
    pymupdf форматирует и вовзращает для отправки в бд"""
    
    pdf_binary = base64.b64decode(book_content)
    pdf_stream = io.BytesIO(pdf_binary)
    doc = fitz.open(stream=pdf_stream, filetype='pdf')
    results = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text('text')
        
        formated_text = format_text_preserve_paragraphs(text)
        results.append({
            'book_id' : book_id,
            'book_name' : book_name,
            'page' : page_num + 1,
            'content' : formated_text,
        })
    doc.close()
    return results


def format_text_preserve_paragraphs(raw_text):
    """
    Форматирует текст, сохраняя абзацы и убирая всё лишнее
    """
    if not raw_text:
        return ""
    # 1. Заменяем множественные переносы строк на двойные (для обозначения абзацев)
    text = re.sub(r'\n{3,}', '\n\n', raw_text) 
    # 2. Убираем лишние пробелы в начале и конце строк
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Убираем пробелы в начале и конце строки
        cleaned_line = line.strip()       
        # Пропускаем полностью пустые строки (кроме тех, что между абзацами)
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
        elif cleaned_lines and cleaned_lines[-1] != "":  # Сохраняем одну пустую строку между абзацами
            cleaned_lines.append("")   
    # 3. Объединяем короткие строки, которые вероятно являются частью одного предложения
    merged_lines = []
    i = 0  
    while i < len(cleaned_lines):
        current_line = cleaned_lines[i]       
        # Если это пустая строка (разделитель абзацев) - сохраняем как есть
        if current_line == "":
            merged_lines.append("")
            i += 1
            continue           
        # Если строка заканчивается на знак конца предложения, оставляем как есть
        if current_line.endswith(('.', '!', '?', ':', ';', '»')):
            merged_lines.append(current_line)
            i += 1
            continue
        # Если следующая строка существует и не пустая, и текущая строка короткая
        if (i + 1 < len(cleaned_lines) and 
            cleaned_lines[i + 1] != "" and
            len(current_line) < 100 and  # Текущая строка короткая
            not cleaned_lines[i + 1][0].isupper()):  # Следующая строка не начинается с заглавной 
            # Объединяем с следующей строкой
            merged_line = current_line + " " + cleaned_lines[i + 1]
            merged_lines.append(merged_line)
            i += 2  # Пропускаем следующую строку, так как объединили
        else:
            merged_lines.append(current_line)
            i += 1
    # 4. Собираем финальный текст
    formatted_text = '\n'.join(merged_lines)
    # 5. Убираем артефакты PDF
    formatted_text = re.sub(r'\x0c', '', formatted_text)  # Убираем символы форматирования
    formatted_text = re.sub(r' +', ' ', formatted_text)   # Убираем множественные пробелы
    return formatted_text.strip()
        

