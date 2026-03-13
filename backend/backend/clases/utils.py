import json
import os
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


HARD_MAX_UPLOAD_BYTES = 1024 * 1024 * 1024  # 1GB


def parse_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            return [parsed]
        except json.JSONDecodeError:
            return [value]
    return [value]


def parse_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {'1', 'true', 'yes', 'si', 'on'}:
            return True
        if lowered in {'0', 'false', 'no', 'off'}:
            return False
    return bool(value)


def normalize_extensions(raw_extensions):
    normalized = []
    for item in parse_list(raw_extensions):
        if item is None:
            continue
        extension = str(item).strip().lower().lstrip('.')
        if extension and extension not in normalized:
            normalized.append(extension)
    return normalized


def save_image_as_webp(image_file, relative_directory, filename_prefix='image', quality=82):
    extension = os.path.splitext(image_file.name)[1].lower().lstrip('.')
    if extension not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f'Extensión no permitida: {extension}')
    if image_file.size > settings.MAX_IMAGE_SIZE:
        raise ValueError('La imagen supera el tamaño permitido')

    try:
        image_file.seek(0)
        with Image.open(image_file) as image:
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')

            output = BytesIO()
            image.save(output, format='WEBP', quality=quality, method=6)
            output.seek(0)
    except (UnidentifiedImageError, OSError):
        raise ValueError('Archivo de imagen inválido')

    relative_path = f"{relative_directory}/{filename_prefix}.webp"
    if default_storage.exists(relative_path):
        default_storage.delete(relative_path)

    return default_storage.save(relative_path, ContentFile(output.read()))
