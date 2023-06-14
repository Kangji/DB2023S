from decimal import Decimal
from typing import Tuple, Dict, Optional

import pymysql
from pymysql import IntegrityError, OperationalError

from datatypes import *
from error import *
from query import *


class Client:
    """Database client. Each method represents a single query."""

    HOST = 'astronaut.snu.ac.kr'
    PORT = 7000
    USER = 'DB2017_18054'
    PASSWD = 'DB2017_18054'
    DB = 'DB2017_18054'
    CHARSET = 'utf8'

    def __init__(self, host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB, charset=CHARSET):
        self.connection = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)

    def __del__(self):
        self.connection.close()

    def begin(self):
        """Begin transaction."""

        self.connection.begin()

    def commit(self):
        """Commit transaction."""

        self.connection.commit()

    def rollback(self):
        """Rollback transaction."""

        self.connection.rollback()

    def create_tables(self):
        """Create tables. Does nothing when tables already exist."""

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_MOVIE)
                cursor.execute(CREATE_USER)
                cursor.execute(CREATE_RESERVATION)
        except OperationalError:  # table already exists
            pass

    def drop_tables(self):
        """Drop tables. Does nothing when the tables do not exist."""

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(DROP_RESERVATION)
                cursor.execute(DROP_USER)
                cursor.execute(DROP_MOVIE)
        except OperationalError:  # table does not exist
            pass

    def select_movie_id(self, movie: Movie) -> Optional[int]:
        """
        Select movie id.

        :return: movie id, or None if movie does not exist.
        """

        with self.connection.cursor() as cursor:
            if cursor.execute(SELECT_MOVIE_ID, movie) == 0:
                return None
            return cursor.fetchone()[0]

    def select_user_id(self, user: User) -> Optional[int]:
        """
        Select user id.

        :return: user id, or None if user does not exist.
        """

        with self.connection.cursor() as cursor:
            if cursor.execute(SELECT_USER_ID, user) == 0:
                return None
            return cursor.fetchone()[0]

    def select_movie_info(self) -> Tuple[Tuple[int, str, str, int, Decimal, int, Decimal], ...]:
        """
        Select movie info.

        :return: table.
        """

        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_MOVIE_INFO)
            return cursor.fetchall()

    def select_user_info(self) -> Tuple[Tuple[int, str, str, Class], ...]:
        """
        Select user info.

        :return: table.
        """

        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_USER_INFO)
            return tuple(r[:3] + (Class.from_discount(r[3]),) for r in cursor.fetchall())  # discount -> class

    def insert_movie(self, movie: Movie):
        """
        Insert a movie.

        :raise MovieAlreadyExists: movie already exists.
        :raise InvalidMoviePrice: invalid movie price.
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(INSERT_MOVIE, movie)
        except IntegrityError:  # unique constraint violation
            raise MovieAlreadyExists(movie.title)
        except OperationalError:  # check constraint violation
            raise InvalidMoviePrice

    def insert_user(self, user: User):
        """
        Insert a user.

        :raise UserAlreadyExists: user already exists.
        :raise InvalidUserAge: invalid user age.
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(INSERT_USER, user)
        except IntegrityError:  # unique constraint violation
            raise UserAlreadyExists(user.name, user.age)
        except OperationalError:  # check constraint violation
            raise InvalidUserAge

    def delete_movie(self, movie_id: int):
        """
        Delete a movie.

        :raise MovieNotExist: movie does not exist.
        """

        with self.connection.cursor() as cursor:
            # 0 rows affected, which means movie does not exist.
            if cursor.execute(DELETE_MOVIE, movie_id) == 0:
                raise MovieNotExist(movie_id)

    def delete_user(self, user_id: int):
        """
        Delete a user.

        :raise UserNotExist: user does not exist.
        """

        with self.connection.cursor() as cursor:
            # 0 rows affected, which means user does not exist.
            if cursor.execute(DELETE_USER, user_id) == 0:
                raise UserNotExist(user_id)

    def insert_reservation(self, reservation: Reservation):
        """
        Insert a reservation.

        :raise MovieNotExist: movie does not exist.
        :raise UserNotExist: user does not exist.
        :raise ReservationAlreadyExists: user has already booked movie.
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(INSERT_RESERVATION, reservation)
        except IntegrityError as e:
            if e.args[0] == 1452:  # referential constraint violation
                if e.args[1].find('`movie_id`') != -1:  # movie_id
                    raise MovieNotExist(reservation.movie_id)
                elif e.args[1].find('`user_id`') != -1:  # user_id
                    raise UserNotExist(reservation.user_id)
            elif e.args[0] == 1062:  # unique constraint violation
                raise ReservationAlreadyExists(reservation.movie_id, reservation.user_id)
            else:  # unknown
                raise e

    def select_reservation(self, movie_id: int):
        """
        Select reservations.

        :raise FullyBooked: movie has already been fully booked.
        """

        with self.connection.cursor() as cursor:
            # Reservation more than 10.
            if cursor.execute(SELECT_RESERVATION, movie_id) > 10:
                raise FullyBooked(movie_id)

    def update_rating(self, rating: Rating) -> bool:
        """
        Update rating.

        :return: whether update succeeded or failed.
        :raise InvalidRating: invalid rating value.
        """

        try:
            with self.connection.cursor() as cursor:
                return cursor.execute(UPDATE_RATING, rating) != 0
        except OperationalError:  # check constraint violation
            raise InvalidRating

    def select_rating(self, reservation: Reservation):
        """
        Select rating.

        :raise MovieNotExist: movie does not exist.
        :raise UserNotExist: user does not exist.
        :raise ReservationNotExist: user has not booked movie yet.
        :raise RatingAlreadyExists: user has already rated movie.
        """

        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_RATING, reservation)
            # Due to outer join, there must be exactly one row.
            movie_opt, user_opt, reservation_opt, rating_opt = cursor.fetchone()

            if movie_opt is None:
                raise MovieNotExist(reservation.movie_id)
            if user_opt is None:
                raise UserNotExist(reservation.user_id)
            if reservation_opt is None:
                raise ReservationNotExist(reservation.movie_id, reservation.user_id)
            if rating_opt is not None:
                raise RatingAlreadyExists(reservation.movie_id, reservation.user_id)

    def select_reserved_users(self, movie_id: int) -> Tuple[Tuple[int, str, int, Decimal, int], ...]:
        """
        Select reserved users.

        :return: table.
        :raise MovieNotExist: movie does not exist.
        """

        with self.connection.cursor() as cursor:
            # Due to outer join, there must be at least one row (null) if movie exists.
            if cursor.execute(SELECT_RESERVED_USERS, movie_id) == 0:
                raise MovieNotExist(movie_id)
            # Filter out null row, produced by outer join.
            return tuple(filter(lambda r: r[0] is not None, cursor.fetchall()))

    def select_reserved_movies(self, user_id: int) -> Tuple[Tuple[int, str, str, Decimal, int], ...]:
        """
        Select reserved movies.

        :return: table.
        :raise UserNotExist: user does not exist.
        """

        with self.connection.cursor() as cursor:
            # Due to outer join, there must be at least one row (null) if user exists.
            if cursor.execute(SELECT_RESERVED_MOVIES, user_id) == 0:
                raise UserNotExist(user_id)
            # Filter out null row, produced by outer join.
            return tuple(filter(lambda r: r[0] is not None, cursor.fetchall()))

    def select_popular_movie(self, user_id: int, target: str) -> Tuple[Tuple[int, str, Decimal, int, Decimal], ...]:
        """
        Select popular movie.

        :return: table.
        :raise UserNotExist: user does not exist.
        """

        target = dict(user_id=user_id, target=target)

        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_POPULAR_MOVIE, target)
            # Due to outer join and limit clause, there must be exactly one row.
            movie_id, title, price, discount, reservation, avg_rating = cursor.fetchone()

        if discount is None:  # user does not exist
            raise UserNotExist(user_id)
        if price is None:  # no more unwatched movie
            return ()
        else:
            return (movie_id, title, price * discount, reservation, avg_rating),

    def select_user(self, user_id: int):
        """
        Select user.

        :raise UserNotExist: user does not exist.
        """

        with self.connection.cursor() as cursor:
            if cursor.execute(SELECT_USER, user_id) == 0:
                raise UserNotExist(user_id)

    def select_rated_user_ids(self) -> Tuple[int, ...]:
        """
        Select rated user ids.

        :return: tuple of user ids corresponding to each row of the matrix.
        """

        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_RATED_USER_IDS)
            return tuple(r[0] for r in cursor.fetchall())

    def select_avg_ratings(self) -> Tuple[Tuple[int, ...], Tuple[Decimal, ...]]:
        """
        Select average ratings.

        :return: tuple of movie_ids and tuple of average ratings corresponding to each column.
        """

        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_AVG_RATINGS)
            records = cursor.fetchall()
            return tuple(r[0] for r in records), tuple(Decimal(0) if r[1] is None else r[1] for r in records)

    def select_all_ratings(self) -> Dict[int, Dict[int, Decimal]]:
        """
        Select all ratings.

        :return: cache (dictionary) of ratings indexed by user id, movie id.
        """

        cache = dict()
        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_RATINGS)
            for i, j, rating in cursor.fetchall():
                if i not in cache:
                    cache[i] = dict()
                cache[i][j] = Decimal(rating)

        return cache

    def select_recommended_movies(self, user_id: int) -> Tuple[Tuple[int, str, Decimal, Decimal], ...]:
        """
        Select recommended movies.

        :return: table.
        """

        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_RECOMMENDED_MOVIES, (user_id, user_id))
            return tuple(
                r[:-1] + (None if r[-1] is None else r[-1].quantize(Decimal('0.01')),)  # round avg rating
                for r in cursor.fetchall()
            )


if __name__ == '__main__':
    # Run before submit project.
    client = Client()
    client.drop_tables()
    client.create_tables()
