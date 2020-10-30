from django import template
from django.core.files.storage import default_storage
import os
from django.conf import settings

register = template.Library()

@register.filter(name='file_exists')
def file_exists(filepath):
    print(filepath)
    print(settings.BASE_DIR)
    print(os.path.join(settings.BASE_DIR, filepath[1:]))
    if default_storage.exists(os.path.join(settings.BASE_DIR, filepath[1:])):
        return filepath
    else:
        index = filepath.rfind('/')
        new_filepath = filepath[:index] + '/image.png'
        return new_filepath
