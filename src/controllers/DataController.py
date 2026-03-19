from .BaseController import BaseController
from fastapi import UploadFile
from models.enums.ResponseEnums import ResponseSignal


class DataController(BaseController):
    size_scaler = 1048576 # convert form mb to b
    def __init__(self ):
        super().__init__()

    def validate_uploaded_file(self,file: UploadFile):
        
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False, ResponseSignal.FILE_TYPE_NOT_ALLOWED.value
        
        if file.size > self.app_settings.FILE_ALLOWED_SIZE * self.size_scaler :
            return False, f"{ResponseSignal.FILE_SIZE_EXCEEDED.value} Allowed size is {self.app_settings.FILE_ALLOWED_SIZE} MB."
        
        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value