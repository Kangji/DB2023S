from decimal import Decimal
from typing import Tuple

import numpy as np
import pandas as pd

from client import Client
from datatypes import *
from error import *
from util import Print

INITIAL_DATA = 'data.csv'
client = Client()


def raises_app_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except AppError as e:
            client.rollback()
            print(e)

    return wrapper


@raises_app_error
def initialize_record(row: Tuple[str, str, str, str, str, str]):
    """Initialize a single record in initial data."""

    title, director, price, name, age, klass = row
    price, age = int(price), int(age)
    try:
        klass = Class(klass)
    except ValueError:
        raise InvalidUserClass

    movie = Movie(title, director, price)
    user = User(name, age, klass)

    client.begin()

    try:
        client.insert_movie(movie)
    except MovieAlreadyExists:
        pass

    try:
        client.insert_user(user)
    except UserAlreadyExists:
        pass

    movie_id = client.select_movie_id(movie)
    user_id = client.select_user_id(user)

    client.insert_reservation(Reservation(movie_id, user_id))
    client.select_reservation(movie_id)  # check if fully booked

    client.commit()


# Problem 1 (5 pt.)
def initialize_database():
    # YOUR CODE GOES HERE
    client.create_tables()

    for _, r in pd.read_csv(INITIAL_DATA).iterrows():
        initialize_record(r)

    print('Database successfully initialized')
    # YOUR CODE GOES HERE
    pass


# Problem 15 (5 pt.)
def reset():
    # YOUR CODE GOES HERE
    if input('Reset database? (y/n) ').lower() == 'y':
        client.drop_tables()
        initialize_database()
    # YOUR CODE GOES HERE
    pass


# Problem 2 (4 pt.)
def print_movies():
    # YOUR CODE GOES HERE
    client.begin()
    records = client.select_movie_info()
    client.commit()

    header = ('id', 'title', 'director', 'price', 'avg. price', 'reservation', 'avg. rating')
    aligns = ('>', '<', '<', '>', '>', '>', '>')
    Print.table(header, aligns, records)
    # YOUR CODE GOES HERE
    pass


# Problem 3 (3 pt.)
def print_users():
    # YOUR CODE GOES HERE
    client.begin()
    records = client.select_user_info()
    client.commit()

    header = ('id', 'name', 'age', 'class')
    aligns = ('>', '<', '>', '<')
    Print.table(header, aligns, records)
    # YOUR CODE GOES HERE
    pass


# Problem 4 (4 pt.)
@raises_app_error
def insert_movie():
    # YOUR CODE GOES HERE
    title = input('Movie title: ')
    director = input('Movie director: ')
    price = int(input('Movie price: '))
    movie = Movie(title, director, price)

    client.begin()
    client.insert_movie(movie)
    client.commit()

    # success message
    print('One movie successfully inserted')
    # YOUR CODE GOES HERE
    pass


# Problem 6 (4 pt.)
@raises_app_error
def remove_movie():
    # YOUR CODE GOES HERE
    movie_id = int(input('Movie ID: '))

    client.begin()
    client.delete_movie(movie_id)
    client.commit()

    # success message
    print('One movie successfully removed')
    # YOUR CODE GOES HERE
    pass


# Problem 5 (4 pt.)
@raises_app_error
def insert_user():
    # YOUR CODE GOES HERE
    try:
        name = input('User name: ')
        age = int(input('User age: '))
        klass = Class(input('User class: '))
        user = User(name, age, klass)
    except ValueError:
        raise InvalidUserClass

    client.begin()
    client.insert_user(user)
    client.commit()

    # success message
    print('One user successfully inserted')
    # YOUR CODE GOES HERE
    pass


# Problem 7 (4 pt.)
@raises_app_error
def remove_user():
    # YOUR CODE GOES HERE
    user_id = int(input('User ID: '))

    client.begin()
    client.delete_user(user_id)
    client.commit()

    # success message
    print('One user successfully removed')
    # YOUR CODE GOES HERE
    pass


# Problem 8 (5 pt.)
@raises_app_error
def book_movie():
    # YOUR CODE GOES HERE
    movie_id = int(input('Movie ID: '))
    user_id = int(input('User ID: '))
    reservation = Reservation(movie_id, user_id)

    client.begin()
    client.insert_reservation(reservation)
    client.select_reservation(movie_id)  # check if fully booked
    client.commit()

    # success message
    print('Movie successfully booked')
    # YOUR CODE GOES HERE
    pass


# Problem 9 (5 pt.)
@raises_app_error
def rate_movie():
    # YOUR CODE GOES HERE
    movie_id = int(input('Movie ID: '))
    user_id = int(input('User ID: '))
    rating = int(input('Ratings (1~5): '))
    rating = Rating(movie_id, user_id, rating)

    client.begin()
    if not client.update_rating(rating):  # 0 rows updated
        # Investigate the reason of failure.
        client.select_rating(rating)  # it will always raise app error
    client.commit()

    # success message
    print('Movie successfully rated')
    # YOUR CODE GOES HERE
    pass


# Problem 10 (5 pt.)
@raises_app_error
def print_users_for_movie():
    # YOUR CODE GOES HERE
    movie_id = int(input('Movie ID: '))

    client.begin()
    records = client.select_reserved_users(movie_id)
    client.commit()

    header = ('id', 'name', 'age', 'res. price', 'rating')
    aligns = ('>', '<', '>', '>', '>')
    Print.table(header, aligns, records)
    # YOUR CODE GOES HERE
    pass


# Problem 11 (5 pt.)
@raises_app_error
def print_movies_for_user():
    # YOUR CODE GOES HERE
    user_id = int(input('User ID: '))

    client.begin()
    records = client.select_reserved_movies(user_id)
    client.commit()

    header = ('id', 'title', 'director', 'res. price', 'rating')
    aligns = ('>', '<', '<', '>', '>')
    Print.table(header, aligns, records)
    # YOUR CODE GOES HERE
    pass


# Problem 12 (6 pt.)
@raises_app_error
def recommend_popularity():
    # YOUR CODE GOES HERE
    user_id = int(input('User ID: '))

    client.begin()
    rating_based = client.select_popular_movie(user_id, 'RB')
    popularity_based = client.select_popular_movie(user_id, 'PB')
    client.commit()

    header = ('id', 'title', 'res. price', 'reservation', 'avg. rating')
    aligns = ('>', '<', '>', '>', '>')
    print('Rating-based')
    Print.table(header, aligns, rating_based)
    print('Popularity-based')
    Print.table(header, aligns, popularity_based)
    # YOUR CODE GOES HERE
    pass


# Problem 13 (10 pt.)
@raises_app_error
def recommend_item_based():
    # YOUR CODE GOES HERE
    user_id = int(input('User ID: '))
    rec_count = int(input('Recommend Count: '))

    client.begin()

    client.select_user(user_id)  # check if user exists
    user_ids = client.select_rated_user_ids()  # row label

    try:
        nrows = len(user_ids)
        row_idx = user_ids.index(user_id)
    except ValueError:  # user has not rated any movie
        raise RatingNotExist

    movie_ids, avg_ratings = client.select_avg_ratings()  # label and avg ratings of columns
    cache = client.select_all_ratings()  # ratings data
    records = client.select_recommended_movies(user_id)  # table without expected ratings

    client.commit()

    ncols = len(movie_ids)
    col_idx = dict((movie_ids[i], i) for i in range(ncols))

    # Create user-movie matrix.
    matrix = np.array(avg_ratings, ndmin=2).repeat(nrows, axis=0)
    for i in range(nrows):
        for j in range(ncols):
            if user_ids[i] in cache and movie_ids[j] in cache[user_ids[i]]:
                matrix[i, j] = cache[user_ids[i]][movie_ids[j]]

    # Calculate similarity matrix.
    mean = matrix.mean()
    diffs = list(matrix[:, j] - mean for j in range(ncols))
    norm_diffs = list(np.linalg.norm(diff) for diff in diffs)
    similarity = np.ndarray((ncols, ncols), dtype=Decimal)
    for i in range(ncols):
        similarity[i, i] = Decimal(0)
        for j in range(i + 1, ncols):
            value = ((diffs[i] * diffs[j]).sum() / norm_diffs[i] / norm_diffs[j]).quantize(Decimal('0.0001'))
            similarity[i, j] = similarity[j, i] = value

    def wavg(col: int) -> Decimal:
        a = matrix[row_idx, :]
        w = similarity[col, :]
        return ((a * w).sum() / w.sum()).quantize(Decimal('0.01'))

    # Append expected ratings to each record and then sort.
    records = list(r + (wavg(col_idx[r[0]]),) for r in records)
    records.sort(key=lambda r: (-r[-1], r[0]))
    records = tuple(records)

    # Done.
    header = ('id', 'title', 'res. price', 'avg. rating', 'expected rating')
    aligns = ('>', '<', '>', '>', '>')
    Print.table(header, aligns, records[:rec_count])
    # YOUR CODE GOES HERE
    pass


# Total of 70 pt.
def main():
    while True:
        print('============================================================')
        print('1. initialize database')
        print('2. print all movies')
        print('3. print all users')
        print('4. insert a new movie')
        print('5. remove a movie')
        print('6. insert a new user')
        print('7. remove an user')
        print('8. book a movie')
        print('9. rate a movie')
        print('10. print all users who booked for a movie')
        print('11. print all movies booked by an user')
        print('12. recommend a movie for a user using popularity-based method')
        print('13. recommend a movie for a user using item-based collaborative filtering')
        print('14. exit')
        print('15. reset database')
        print('============================================================')
        menu = int(input('Select your action: '))

        if menu == 1:
            initialize_database()
        elif menu == 2:
            print_movies()
        elif menu == 3:
            print_users()
        elif menu == 4:
            insert_movie()
        elif menu == 5:
            remove_movie()
        elif menu == 6:
            insert_user()
        elif menu == 7:
            remove_user()
        elif menu == 8:
            book_movie()
        elif menu == 9:
            rate_movie()
        elif menu == 10:
            print_users_for_movie()
        elif menu == 11:
            print_movies_for_user()
        elif menu == 12:
            recommend_popularity()
        elif menu == 13:
            recommend_item_based()
        elif menu == 14:
            print('Bye!')
            break
        elif menu == 15:
            reset()
        else:
            print('Invalid action')


if __name__ == "__main__":
    main()
