from typing import List
from pydantic import Field
from app.routers.admin.crud.schemas import NameMixin, EntityMixin, ListResponseMixin
class StateBase(NameMixin):
    code: str = Field(min_length=1, max_length=10)
    country_id: str = Field(min_length=36, max_length=36)
class StateCreate(StateBase):
    pass
class StateUpdate(StateBase):
    pass
class StateWithCountry(StateBase, EntityMixin):
    country: dict
class StateList(ListResponseMixin):
    list: List[StateWithCountry]
