from typing import List
from dataclasses import dataclass, field

@dataclass
class Person:
    id: int
    name: str
    birth_date: str
    partners: List[str] = field(default_factory=list)
    parents: List[str] = field(default_factory=list)
    kids: List[str] = field(default_factory=list)

    @property
    def birth_year(self) -> int:
        try:
            return int(self.birth_date.split("-")[0])
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