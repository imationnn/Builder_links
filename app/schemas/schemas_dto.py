from dataclasses import dataclass, field


@dataclass(slots=True)
class XsubjectDTO:
    id: int
    count: int
    name: str

    @classmethod
    def from_dict(cls, data: dict):
        filtered_data = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**filtered_data)


@dataclass
class SubCategoryDTO:
    name: str
    query: str
    shard: str
    url: str
    xsubjects: list[XsubjectDTO] = field(default_factory=list)
    total: int = 0

    @classmethod
    def from_dict(cls, data: dict):
        filtered_data = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**filtered_data)


@dataclass(slots=True)
class CategoryDTO:
    category: str
    sub_cat_dto: list[SubCategoryDTO]


@dataclass(slots=True)
class NotifyItem:
    category_name: str
    subcategory: str = None
    xsubject: int = None
