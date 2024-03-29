create table audit_log
(
    id                int auto_increment
        primary key,
    event_datetime    datetime    not null,
    username          varchar(45) not null,
    event_description varchar(45) not null
);

create table users
(
    id                 int auto_increment
        primary key,
    username           varchar(45)       not null,
    password           varchar(45)       not null,
    login_attempts     int     default 0 null,
    locked             tinyint default 0 null,
    rools              tinyint default 0 null,
    unlock_time        timestamp         null,
    last_login_attempt timestamp         null
);

create index username_idx
    on users (username);