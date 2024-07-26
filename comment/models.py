from django.core.validators import FileExtensionValidator
from django.db import models

import re
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

from PIL import Image


@deconstructible
class HTMLValidator:
    """Валидатор для HTML-тегов"""

    def __init__(self, allowed_tags):
        self.allowed_tags = allowed_tags
        self.tag_re = re.compile(r'<(/?)(\w+).*?>', re.IGNORECASE)

    def __call__(self, value):
        stack = []
        tags = self.tag_re.findall(value)

        for is_closing, tag_name in tags:
            if tag_name not in self.allowed_tags:
                raise ValidationError(f"Тэг '{tag_name}' запрещен.")

            if is_closing:
                if not stack or stack[-1] != tag_name:
                    raise ValidationError(f"Неправильное закрытие тэга '{tag_name}'.")
                stack.pop()
            else:
                stack.append(tag_name)

        if stack:
            raise ValidationError("Некоторые теги не закрыты правильно.")

    def __eq__(self, other):
        return isinstance(other, HTMLValidator) and self.allowed_tags == other.allowed_tags


allowed_tags = ['a', 'code', 'i', 'strong']
html_validator = HTMLValidator(allowed_tags)


def validate_image(image):
    max_width, max_height = 320, 240
    img = Image.open(image)
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.LANCZOS)
        img.save(image.path)


def validate_text_file(text_file):
    if text_file.size > 100 * 1024:
        raise ValidationError("Размер файла должен быть меньше 100KB")


class Comment(models.Model):
    """Модель комментария"""
    username = models.CharField(max_length=150)
    email = models.EmailField()
    homepage = models.URLField(blank=True, null=True)
    message = models.TextField(validators=[html_validator])
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True,
                              validators=[FileExtensionValidator(['jpg', 'gif', 'png'])])
    text_file = models.FileField(upload_to='text_files/', blank=True, null=True,
                                 validators=[FileExtensionValidator(['txt'])])

    def get_children(self):
        return self.children.all().order_by('-date')

    def __str__(self):
        parent_username = self.parent.username if self.parent else 'No parent'
        return f'{parent_username} to {self.username} - {self.date}'

    def save(self, *args, **kwargs):
        if self.image:
            validate_image(self.image)
        if self.text_file:
            validate_text_file(self.text_file)
        super().save(*args, **kwargs)
