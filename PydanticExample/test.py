from datetime import date

from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    birthday: date

    def __str__(self):
        return f'User(id={self.id}, name={self.name}, birthday={self.birthday})'

try :
    print( User(id=1, name='John', birthday=date(2000, 1, 1)) )
except Exception as e:
    print(e)

try :
    print( User(id='u_id', name='John', birthday=date(2000, 1, 1)) )
except Exception as e:
    print(e)