from datetime import datetime

from beanie import Document, Indexed


class User(Document):
    name: str
    email: Indexed(str, unique=True)
    password: str
    created_at: datetime

    @property
    def id_str(self):
        return str(self.id)
