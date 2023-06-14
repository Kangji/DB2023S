####################################################################################################
# Data Definition Language
####################################################################################################

CREATE_MOVIE = """
create table movie(
    id int primary key auto_increment,
    title varchar(255) not null unique,
    director varchar(255) not null,
    price int not null check (price between 0 and 100000)
);
"""
CREATE_USER = """
create table user(
    id int primary key auto_increment,
    name varchar(255) not null,
    age int not null check (age between 12 and 110),
    discount float not null,
    unique (name, age)
);
"""
CREATE_RESERVATION = """
create table reservation(
    movie_id int not null,
    user_id int not null,
    rating int check (rating between 1 and 5),
    foreign key (movie_id) references movie (id) on delete cascade,
    foreign key (user_id) references user (id) on delete cascade,
    unique (movie_id, user_id)
);
"""

DROP_MOVIE = """
drop table movie;
"""
DROP_USER = """
drop table user;
"""
DROP_RESERVATION = """
drop table reservation;
"""

####################################################################################################
# 1. Initialization
####################################################################################################

SELECT_MOVIE_ID = """
select id from movie where title = %(title)s;
"""
SELECT_USER_ID = """
select id from user where name = %(name)s and age = %(age)s;
"""

####################################################################################################
# 2. Movie Info
####################################################################################################

SELECT_MOVIE_INFO = """
select movie.id, title, director, price, avg(price * discount), count(user_id), avg(rating)
from movie left outer join reservation on movie.id = movie_id left outer join user on user.id = user_id
group by title
order by movie.id;
"""

####################################################################################################
# 3. User Info
####################################################################################################

SELECT_USER_INFO = """
select id, name, age, discount from user
order by id;
"""

####################################################################################################
# 4. Add Movie
####################################################################################################

INSERT_MOVIE = """
insert into movie (title, director, price)
values (%(title)s, %(director)s, %(price)s);
"""

####################################################################################################
# 5. Add User
####################################################################################################

INSERT_USER = """
insert into user (name, age, discount)
values (%(name)s, %(age)s, %(discount)s);
"""

####################################################################################################
# 6. Delete Movie
####################################################################################################

DELETE_MOVIE = """
delete from movie where id = %s;
"""

####################################################################################################
# 7. Delete User
####################################################################################################

DELETE_USER = """
delete from user where id = %s;
"""

####################################################################################################
# 8. Add Reservation
####################################################################################################

INSERT_RESERVATION = """
insert into reservation (movie_id, user_id)
values (%(movie_id)s, %(user_id)s);
"""
SELECT_RESERVATION = """
select user_id from reservation
where movie_id = %s;
"""

####################################################################################################
# 9. Add Rating
####################################################################################################

UPDATE_RATING = """
update reservation
set rating = %(rating)s
where rating is null and movie_id = %(movie_id)s and user_id = %(user_id)s;
"""
SELECT_RATING = """
select movie.id, user.id, movie_id, rating
from (select %(movie_id)s mid, %(user_id)s uid) L
    left outer join movie on L.mid = movie.id
    left outer join user on L.uid = user.id
    left outer join reservation on L.mid = movie_id and L.uid = user_id;
"""

####################################################################################################
# 10. Reserved Users
####################################################################################################

SELECT_RESERVED_USERS = """
select user.id, name, age, price * discount, rating
from (select id, price from movie where id = %s) M
    left outer join reservation on M.id = movie_id
    left outer join user on user_id = user.id
order by user.id;
"""

####################################################################################################
# 11. Reserved Movies
####################################################################################################

SELECT_RESERVED_MOVIES = """
select movie.id, title, director, price * discount, rating
from (select id, discount from user where id = %s) U
    left outer join reservation on U.id = user_id
    left outer join movie on movie_id = movie.id
order by movie.id;
"""

####################################################################################################
# 12. Popularity Based Recommendation
####################################################################################################

SELECT_POPULAR_MOVIE = """
select M.id, title, price, discount, `'PB'`, `'RB'`
from (select %(user_id)s uid) L left outer join user on L.uid = user.id
    left outer join (select %(user_id)s uid, id, title, price, count(user_id) `'PB'`, avg(rating) `'RB'`
        from movie left outer join reservation on id = movie_id
        where id not in (select movie_id from reservation where user_id = %(user_id)s)
        group by title) M
    on L.uid = M.uid
order by `%(target)s` desc, id
limit 1;
"""

####################################################################################################
# 13. Item Based Recommendation
####################################################################################################

SELECT_USER = """
select 1 from user where id = %s;
"""
SELECT_RATED_USER_IDS = """
select distinct user_id from reservation
where rating is not null
order by user_id;
"""
SELECT_AVG_RATINGS = """
select movie.id, avg(rating)
from movie left outer join reservation on id = movie_id
group by movie.id
order by movie.id;
"""
SELECT_ALL_RATINGS = """
select user_id, movie_id, rating from reservation
where rating is not null;
"""
SELECT_RECOMMENDED_MOVIES = """
select id, title, price * (select discount from user where id = %s), avg(rating)
from movie left outer join reservation on id = movie_id
where id not in (select movie_id from reservation where user_id = %s)
group by title;
"""
