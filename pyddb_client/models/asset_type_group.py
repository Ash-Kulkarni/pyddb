from pydantic import BaseModel


class AssetTypeGroup(BaseModel):
    id: str
    name: str

    def __repr__(self) -> str:
        return repr(f"Name: {self.name}, id: {self.id}")
