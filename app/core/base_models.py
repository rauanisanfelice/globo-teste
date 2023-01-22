from datetime import datetime

from core.serializers import to_camel
from pydantic import BaseConfig, BaseModel


class EntityModel(BaseModel):
    """Base class for all models."""

    class Config(BaseConfig):
        alias_generator = to_camel
        allow_mutation = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda x: x.strftime("%Y-%m-%dT%H:%M:%SZ")}
