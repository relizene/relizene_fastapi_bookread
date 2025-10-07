from bson import ObjectId
import pymupdf
import base64
import os
from pymongo import MongoClient


def delete_file(remove_name):
    """Удаление файла для очистки памяти"""
    os.remove(f'{remove_name}.pdf')
  

def pdf_formater(book_content, book_name, book_id):
    """Берет данные закодированные в base 64, затем сохраняет его в пдф файл и с помощью
    pymupdf форматирует и вовзращает для отправки в бд"""
    
    pdf_binary = base64.b64decode(book_content)
    with open(f'{book_name}.pdf', 'wb') as file:
        file.write(pdf_binary)
        file.flush()
           
    doc = pymupdf.open(f'{book_name}.pdf')
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
    return results
        


   
    
"""Все связано тестами"""  
def code():
    """Закодирование в формат base 64"""
    with open('Fillips.pdf' , 'rb') as fp:
        binary = base64.b64encode(fp.read())
        return binary
def test_2():
    uri = 'mongodb://root:example@localhost:27017/'
    client = MongoClient(uri)
    db = client['book_library']
    books_collection = db.book
    books_pages = db.pages
    
    data = {
        'book_name' : 'Fillips',
    }
    id_back = books_collection.insert_one(data).inserted_id
    if id_back:
        first = code()
        result = pdf_formater(first, 'Fillips', id_back)
        books_pages.insert_many(result)
    
def test_3():
    uri = 'mongodb://root:example@localhost:27017/'
    client = MongoClient(uri)
    db = client['book_library']
    books_collection = db.book
    books_pages = db.pages
    
    page = books_pages.find_one({'book_id' : ObjectId('68e3c51a36bfb0645555a2ed'), 'page' : 160})
    return page
if __name__ == '__main__':
    test_2()
    
    
    
