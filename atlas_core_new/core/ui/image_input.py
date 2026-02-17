"""
atlas_core/core/ui/image_input.py

Image input processing.
"""

from fastapi import UploadFile


async def describe_image_stub(img: UploadFile) -> str:
    return f"(image description stub) image='{img.filename}'"
