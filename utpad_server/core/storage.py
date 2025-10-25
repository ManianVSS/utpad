import os

from django.core.files.storage import FileSystemStorage


class CustomFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            available_name = super().get_available_name(name, max_length)
            os.rename(os.path.join(self.location, name), os.path.join(self.location, available_name))
        return name
