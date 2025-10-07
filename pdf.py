import fitz
import base64
import os
from pymongo import MongoClient


def pdf_formater(book_content, book_name, book_id):
    """Берет данные закодированные в base 64, затем сохраняет его в пдф файл и с помощью
    pymupdf форматирует и вовзращает для отправки в бд"""
    
    pdf_binary = base64.b64decode(book_content)
    with open(f'{book_name}.pdf', 'wb') as file:
        file.write(pdf_binary)
        file.flush()
           
    doc = fitz.open(f'{book_name}.pdf')
    results = []
    count = 0
    for page in doc:
        count += 1
        text = page.get_text('html')
        results.append({
            'book_id' : book_id,
            'book_name' : book_name,
            'page' : count,
            'content' : text,
        })
    doc.close()
    return results
        
def delete_file(remove_name):
    """Удаление файла для очистки памяти"""
    os.remove(f'{remove_name}.pdf')
    
