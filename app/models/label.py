from pydantic import BaseModel,Field

class LabelData(BaseModel):
    product_name: str|None=None
    ingredients:list[str]=Field(default_factory=list)
    claims:list[str]=Field(default_factory=list)
    warnings:list[str]=Field(default_factory=list)
    usage_instructions:list[str]=Field(default_factory=list)
    manufacturer:str|None=None
    raw_text:str