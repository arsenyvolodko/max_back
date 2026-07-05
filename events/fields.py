import hashlib
import os

from django.db import models


def file_content_hash(fileobj, length=8, chunk_size=65536):
    """SHA-256 содержимого файла, усечённый до `length` символов."""
    hasher = hashlib.sha256()
    can_seek = hasattr(fileobj, 'seek')
    pos = fileobj.tell() if can_seek and hasattr(fileobj, 'tell') else 0
    if can_seek:
        fileobj.seek(0)
    for chunk in iter(lambda: fileobj.read(chunk_size), b''):
        if isinstance(chunk, str):
            chunk = chunk.encode()
        hasher.update(chunk)
    if can_seek:
        fileobj.seek(pos)
    return hasher.hexdigest()[:length]


class HashedFileField(models.FileField):
    """FileField, дописывающий `_<хеш содержимого>` в конец имени файла.

    Хеш считается только для новых (ещё не сохранённых) файлов, поэтому при
    изменении содержимого имя — а значит и URL — гарантированно меняется,
    независимо от исходного имени.
    """

    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)
        if file and not file._committed and file.name:
            base, ext = os.path.splitext(os.path.basename(file.name))
            digest = file_content_hash(file.file)
            file.name = f'{base}_{digest}{ext}'
        return super().pre_save(model_instance, add)
