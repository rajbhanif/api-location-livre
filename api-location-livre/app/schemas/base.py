from pydantic import BaseModel, ConfigDict
from app.utils.naming import to_camel

class APIModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )
