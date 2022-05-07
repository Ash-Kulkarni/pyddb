from pydantic import BaseModel


class Staff(BaseModel):
    staff_id: int
    staff_name: str
    email: str
    company_centre_arup_unit: str
    location_name: str
    grade_level: int
    my_people_page_url: str

    def __repr__(self) -> str:
        return repr(f"Name: {self.staff_name}")
