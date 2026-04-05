from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATION_SUCCESS = "File is valid ."
    FILE_TYPE_NOT_ALLOWED = "File type is not allowed."
    FILE_SIZE_EXCEEDED = "File size exceeded the allowed limit."
    FILE_UPLOAD_SUCCESS = "File uploaded successfully."
    FILE_UPLOAD_FAILED = "File upload failed."


    FILE_PROCESSING_SUCCESS = "File processed successfully."
    FILE_PROCESSING_FAILED = "File processing failed."
    NO_FILES_TO_PROCESS = "No files to process for the given project."

    FILE_NOT_FOUND_WITH_THIS_ID = "No file found with the provided file_id in the project."