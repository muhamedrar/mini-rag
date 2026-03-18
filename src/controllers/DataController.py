from .BaseController import BaseController
from fastapi import UploadFile


class DataController(BaseController):
    size_scaler = 1048576 # convert form mb to b
    def __init__(self ):
        super().__init__()

    def validate_uploaded_file(self,file: UploadFile):
        print(file.content_type)
        print(self.app_settings.FILE_ALLOWED_TYPE)
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False, f"File type {file.content_type} is not allowed"
        
        if file.size > self.app_settings.FILE_ALLOWED_SIZE * self.size_scaler :
            return False , f"File size {file.size} exceeds the allowed limit of {self.app_settings.FILE_ALLOWED_SIZE} MB"
        
        return True, "File is valid"