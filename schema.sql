drop table if exists entries;
create table entries (
    id integer primary key autoincrement,
    title text not null,
    'text' text not null
);
DROP TABLE IF EXISTS admin_messages;
CREATE TABLE admin_messages(
    id integer primary key autoincrement,
    content text not null,
    ipaddress text not null,
    currenttime text not null
);
DROP TABLE IF EXISTS projects_entries;
CREATE TABLE projects_entries(
    id integer primary key autoincrement,
    project_title text not null,
    project_content text not null
);
DROP TABLE IF EXISTS captions;
CREATE TABLE captions(
    id integer primary key autoincrement,
    caption text not null,
    imagepath text not null
);