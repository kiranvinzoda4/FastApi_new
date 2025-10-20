from typing import List
from pydantic import Field
from app.routers.admin.crud.schemas import NameMixin, EntityMixin, ListResponseMixin


class CountryBase(NameMixin):
    code: str = Field(min_length=1, max_length=10)


class CountryCreate(CountryBase):
    pass


class CountryUpdate(CountryBase):
    pass


class Country(CountryBase, EntityMixin):
    pass


class CountryList(ListResponseMixin):
    list: List[Country]