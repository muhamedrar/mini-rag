from pydantic import BaseModel
from typing import Optional



class NlpPushSchema(BaseModel):
    do_reset : Optional[int] = 0


class NlpSchemaSearch(BaseModel):
    query: str
    limit: Optional[int] = 5