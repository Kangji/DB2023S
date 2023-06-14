from abc import ABCMeta, abstractmethod


class AppError(Exception, metaclass=ABCMeta):
    """Top-level application error."""

    def __str__(self):
        return self.msg()

    @staticmethod
    @abstractmethod
    def msg():
        pass


class MovieAlreadyExists(AppError):
    def __init__(self, title: str):
        self.title = title

    def msg(self):
        return f'Movie {self.title} already exists'


class UserAlreadyExists(AppError):
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def msg(self):
        return f'User ({self.name}, {self.age}) already exists'


class ReservationAlreadyExists(AppError):
    def __init__(self, movie_id: int, user_id: int):
        self.movie_id = movie_id
        self.user_id = user_id

    def msg(self):
        return f'User {self.user_id} has already booked movie {self.movie_id}'


class RatingAlreadyExists(AppError):
    def __init__(self, movie_id: int, user_id: int):
        self.movie_id = movie_id
        self.user_id = user_id

    def msg(self):
        return f'User {self.user_id} has already rated movie {self.movie_id}'


class MovieNotExist(AppError):
    def __init__(self, movie_id: int):
        self.id = movie_id

    def msg(self):
        return f'Movie {self.id} does not exist'


class UserNotExist(AppError):
    def __init__(self, user_id: int):
        self.id = user_id

    def msg(self):
        return f'User {self.id} does not exist'


class ReservationNotExist(AppError):
    def __init__(self, movie_id: int, user_id: int):
        self.movie_id = movie_id
        self.user_id = user_id

    def msg(self):
        return f'User {self.user_id} has not booked movie {self.movie_id} yet'


class RatingNotExist(AppError):
    @staticmethod
    def msg():
        return 'Rating does not exist'


class InvalidMoviePrice(AppError):
    @staticmethod
    def msg():
        return 'Movie price should be from 0 to 100000'


class InvalidUserAge(AppError):
    @staticmethod
    def msg():
        return 'User age should be from 12 to 110'


class InvalidUserClass(AppError):
    @staticmethod
    def msg():
        return 'User class should be basic, premium or vip'


class InvalidRating(AppError):
    @staticmethod
    def msg():
        return 'Wrong value for a rating'


class FullyBooked(AppError):
    def __init__(self, movie_id: int):
        self.id = movie_id

    def msg(self):
        return f'Movie {self.id} has already been fully booked'
