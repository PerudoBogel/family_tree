from typing import List
from dataclasses import dataclass, field

@dataclass
class Person:
    id: int
    name: str
    birth_date: str
    partners: List[int] = field(default_factory=list)
    parents: List[int] = field(default_factory=list)
    kids: List[int] = field(default_factory=list)

    @property
    def birth_year(self) -> str:
        try:
            return self.birth_date.split("-")[0]
        except Exception:
            return 0
    
    @property
    def name_n_birth(self) -> str:
        try:
            return self.name + "(" + str(self.birth_year) + ")"
        except Exception:
            return 0

    @classmethod
    def from_dict(cls, data: dict) -> "Person":
        return cls(
            id=data["id"],
            name=data["name"],
            birth_date=data["birth_date"],
            partners=data.get("partners", []),
            parents=data.get("parents", []),
            kids=data.get("kids", [])
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "birth_date": self.birth_date,
            "partners": self.partners,
            "parents": self.parents,
            "kids": self.kids
        }