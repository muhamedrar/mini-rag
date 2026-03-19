from .BaseController import BaseController
from fastapi import UploadFile
from models.enums.ResponseEnums import ResponseSignal
from .ProjectContoller import ProjectController
import  re ,os


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
    

    def generate_unique_filename(self,original_string: str, project_id: str):
        random_key =self.generate_unique_string()
        cleaned_original_string = self.cleaned_filename(original_string)
        project_dir_path = ProjectController().get_project_path(project_id)
        unique_file_path = os.path.join(
            project_dir_path,
              random_key + "_" + cleaned_original_string
            )

        while  os.path.exists(unique_file_path):
            random_string =self.generate_unique_string()
            cleaned_original_string = self.cleaned_filename(original_string)
            project_dir_path = ProjectController().get_project_path(project_id)
            unique_file_path = os.path.join(
                project_dir_path,
                random_key + "_" + cleaned_original_string
                )
        return unique_file_path

    def cleaned_filename(self,original_file_name: str):
        cleaned_name = re.sub(r'[^\w\.-]', '_', original_file_name.strip())
        cleaned_name = re.sub(' ', '_', cleaned_name)
        return cleaned_name
