from enum import Enum


class Class(Enum):
    """Mapping between class and discount rate."""

    BASIC = 'basic'
    PREMIUM = 'premium'
    VIP = 'vip'

    def __str__(self):
        return self.value

    def discount(self):
        if self is self.BASIC:
            return 1.0
        elif self is self.PREMIUM:
            return 0.75
        else:
            return 0.5

    @classmethod
    def from_discount(cls, discount: float):
        if discount == 0.5:
            return cls.VIP
        elif discount == 0.75:
            return cls.PREMIUM
        else:
            return cls.BASIC


class Movie(dict):
    """Movie."""

    __slots__ = 'title', 'director', 'price'

    def __init__(self, title: str, director: str, price: int):
        super().__init__()
        self.title = self['title'] = title
        self.director = self['director'] = director
        self.price = self['price'] = price


class User(dict):
    """User."""

    __slots__ = 'name', 'age', 'discount'

    def __init__(self, name: str, age: int, klass: Class):
        super().__init__()
        self.name = self['name'] = name
        self.age = self['age'] = age
        self.discount = self['discount'] = klass.discount()


class Reservation(dict):
    """Reservation."""

    __slots__ = 'movie_id', 'user_id'

    def __init__(self, movie_id: int, user_id: int):
        super().__init__()
        self.movie_id = self['movie_id'] = movie_id
        self.user_id = self['user_id'] = user_id


class Rating(Reservation):
    """Rating."""

    __slots__ = 'rating'

    def __init__(self, movie_id: int, user_id: int, rating: int):
        super().__init__(movie_id, user_id)
        self.rating = self['rating'] = rating
