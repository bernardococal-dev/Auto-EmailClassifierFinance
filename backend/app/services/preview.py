import os
import base64
from PIL import Image
import pdfplumber

STORAGE_DIR = os.environ.get('STORAGE_DIR', '/data/storage')

os.makedirs(STORAGE_DIR, exist_ok=True)


def generate_preview(file_path: str, max_width: int = 1200) -> str:
    """Generate a preview image (PNG) for a PDF or image and return base64 string of the preview.
    Stores preview next to file as <file>.preview.png
    """
    out_path = file_path + '.preview.png'

    if file_path.lower().endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            page = pdf.pages[0]
            img = page.to_image(resolution=150)
            pil = img.original
            pil.thumbnail((max_width, max_width))
            pil.save(out_path, format='PNG')
    else:
        with Image.open(file_path) as im:
            im.thumbnail((max_width, max_width))
            im.save(out_path, format='PNG')

    with open(out_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return data
