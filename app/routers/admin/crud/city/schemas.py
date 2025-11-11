from typing import List
from pydantic import Field
from app.routers.admin.crud.schemas import NameMixin, EntityMixin, ListResponseMixin


class CityBase(NameMixin):
    state_id: str = Field(min_length=36, max_length=36)


class CityCreate(CityBase):
    pass


class CityUpdate(CityBase):
    pass


class CityWithState(CityBase, EntityMixin):
    state: dict


class CityList(ListResponseMixin):
    list: List[CityWithState]
