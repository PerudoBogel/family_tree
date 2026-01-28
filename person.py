from typing import List
from dataclasses import dataclass, field

@dataclass
class Person:
    id: int
    name: str
    middle_name: str
    last_name: str
    family_name: str
    birth_date: str
    death_date: str
    notes: str
    photo_source: str
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
        
        def get_str_non_interupt(name: str):
            val = ""
            try:
                val = data[name]
            except:
                pass
            return val
        
        def get_array_non_interupt(name: str):
            val = []
            try:
                val = data.get(name,[])
            except:
                pass
            return val

        name=get_str_non_interupt("name")
        middle_name=get_str_non_interupt("middle_name")
        last_name=get_str_non_interupt("last_name")
        family_name=get_str_non_interupt("family_name")
        birth_date=get_str_non_interupt("birth_date")
        death_date=get_str_non_interupt("death_date")
        notes=get_str_non_interupt("notes")
        photo_source=get_str_non_interupt("photo_source")
        partners=get_array_non_interupt("partners")
        parents=get_array_non_interupt("parents")
        kids=get_array_non_interupt("kids")

        return cls(
            id=data["id"],
            name=name,
            middle_name=middle_name,
            last_name=last_name,
            family_name=family_name,
            birth_date=birth_date,
            death_date=death_date,
            notes=notes,
            photo_source=photo_source,
            partners=partners,
            parents=parents,
            kids=kids
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "family_name": self.family_name,
            "birth_date": self.birth_date,
            "death_date": self.death_date,
            "notes": self.notes,
            "photo_source": self.photo_source,
            "partners": self.partners,
            "parents": self.parents,
            "kids": self.kids
        }