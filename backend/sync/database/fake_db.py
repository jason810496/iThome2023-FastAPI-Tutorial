fake_db = {
    "users": 
        [
            {
                "id": 1,
                "password": "John",
                "avatar": "https://i.pravatar.cc/300",
                "name": "John",
                "age": 35,
                "email": "john@fakemail.com",
                "birthday": "2000-01-01",
            },
            {
                "id": 2,
                "password": "Jane",
                "avatar": None,
                "name": "Jane",
                "age": 25,
                "email": "jane@fakemail.com",
                "birthday": "2010-12-04",
            }
        ]
    ,
    "items": 
        [
            {
                "id": 1,
                "name": "iPhone 12",
                "price": 1000,
                "brand": "Apple"
            },
            {
                "id": 2,
                "name": "Galaxy S21",
                "price": 800,
                "brand": "Samsung"
            }
        ]
    ,
}

def get_db():
    return fake_db