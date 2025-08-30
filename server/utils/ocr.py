from __future__ import annotations
from typing import Optional
from PIL import Image
import pytesseract

def ocr_image(path: str) -> str:
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception:
        return "[ocr_unavailable]"
