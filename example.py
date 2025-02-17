from markitdown import MarkItDown


md = MarkItDown()

res = md.convert('lib/db.py')

print(res.text_content)
