-- CREATE TABLE
-- success
create table foo(
    id int,
    name char(10),
    dob date,
    primary key (id),
    foreign key (id) references foo (id)
);

create table bar(
    id int,
    foreign key (id) references foo (id)
);

-- DuplicateColumnDefError
create table fail(
    id int,
    id char(10)
);

-- TableExistenceError
create table foo(id int);

-- CharLengthError
create table fail(name char(0));

-- DuplicatePrimaryKeyDefError
create table fail(
    id int,
    idd int,
    primary key (id),
    primary key (idd)
);

-- NonExistingColumnDefError(name)
create table fail(
    id int,
    primary key (name)
);

create table fail(
    id int,
    foreign key (name) references foo (name)
);

-- ReferenceTypeError
create table fail(
    id int,
    name char(10),
    foreign key (name) references fail (id)
);

create table fail(
    id int,
    name char(10),
    foreign key (id, name) references fail (name, id)
);

create table fail(
    id int,
    name char(10),
    foreign key (id, name) references fail (id)
);

create table fail(
    name char(10),
    named char(5),
    foreign key (named) references fail (name)
);

-- ReferenceNonPrimaryKeyError
create table fail(
    id int,
    foreign key (id) references fail (id)
);

create table fail(
    id int,
    idd int,
    primary key (id, idd),
    foreign key (idd, id) references fail (idd, id)
);

-- ReferenceColumnExistenceError
create table fail(
    id int,
    foreign key (id) references foo (hello)
);

-- ReferenceTableExistenceError
create table fail(
    id int,
    foreign key (id) references baz (id)
);

-- DROP TABLE
create table baz(
    id int,
    primary key (id),
    foreign key (id) references baz (id)
);
create table alice(
    id int,
    foreign key (id) references baz (id)
);

-- DropReferencedTableError(baz)
drop table baz;

-- success
drop table alice;
drop table baz;

-- NoSuchTable
drop table baz;

-- EXPLAIN, DESC, DESCRIBE
-- id must be not null
explain foo;

desc foo;
describe bar;

-- INSERT
-- success
insert into foo values (1, 'Jiho', 1998-12-03);
insert into foo (id, name) values (2, 'Joon');
insert into foo (id, name) values (3, null);

-- NoSuchTable
insert into baz values (1);

-- InsertColumnExistenceError(hello)
insert into foo (hello) values (3);

-- InsertTypeMismatchError
insert into foo values (1);
insert into foo (id) values ('JihoJihoJihoJiho');

-- InsertColumnNonNullableError(id)
insert into foo (id) values (null);

-- DELETE
-- success
-- 0 row(s)
delete from bar;

-- 2 row(s)
insert into bar values (3);
insert into bar values (4);
delete from bar;

-- 1 row(s)
insert into bar values (3);
insert into bar values (4);
delete from bar where id = 4;

-- NoSuchTable
delete from baz;

-- SELECT
-- success - select
-- foo.id - 1 - 2 - 3
select foo.id from foo;
-- id - 1 - 2 - 3
select id from foo;
-- id - 3
select * from bar;

-- success - from
-- (foo.id, name, dob, bar.id) - 6 rows
insert into bar values (4);
select * from foo, bar;

-- success - where
select id from foo where dob is null;
-- id - 2 - 3

select id from foo where foo.name is null;
-- id - 3

select id from foo where id is not null;
-- id - 1 - 2 - 3

select id from foo where foo.id is null;
-- id

select * from bar where null is null;
-- id - 3 - 4

select * from bar where 3 is null;
-- id

select * from bar where 3 is not null;
-- id - 3 - 4

select * from bar where 'Jiho' is null;
-- id

select * from bar where 'Jiho' is not null;
-- id - 3 - 4

select * from bar where 1998-12-03 is not null;
-- id - 3 - 4

select * from bar where id = id;
-- id - 3 - 4

select * from bar where id = 3;
-- id - 3

select * from bar where id = null;
-- id

select id from foo where name = 'Jiho';
-- id - 1

select id from foo where name = null;
-- id

select id from foo where name = name;
-- id - 1 - 2

select id from foo where dob = dob;
-- id - 1

select id from foo where dob != dob;
-- id

select id from foo where 3 = id;
-- id - 3

select id from foo where not null = null;
-- id

select id from foo where id > 1 and name is null;
-- id - 3

select id from foo where id >= 1 and id <= 2;
-- id - 1 - 2

select id from foo where id = 1 or id = 2;
-- id - 1 - 2

select id from foo where (id = 1 or id = 2) and id = 2;
-- id - 2

select id from foo where id = 1 or id = 2 and id = 2;
-- id - 1 - 2

-- SelectColumnResolveError
select id from foo, bar;

select f.id from foo;

-- SelectTableExistenceError(baz)
select * from baz;

-- WhereIncomparableError
select * from foo where id = 'Jiho';
select * from foo where id = 1998-12-03;
select * from foo where name = 3;

-- WhereTableNotSpecified
select * from foo where baz.id = 3;

-- WhereColumnNotExist
select * from foo where bar = 3;

-- WhereAmbiguousReference
select * from foo, bar where id = 3;

-- SHOW TABLES
show tables;

-- EXIT
exit;
