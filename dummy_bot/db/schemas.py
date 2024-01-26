from pydantic import BaseModel


class UserDTO(BaseModel):
    id: int
    username: str
    fullname: str


class PokakStatDTO(BaseModel):
    id: int
    user: UserDTO
