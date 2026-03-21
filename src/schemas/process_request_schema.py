from pydantic import BaseModel
from typing import Optional

class ProcessRequestSchema(BaseModel):
    file_id : str
    chunk_size : Optional[int] = 50
    ovelap_size : Optional[int] = 10
    do_reset : Optional[int] = 0
