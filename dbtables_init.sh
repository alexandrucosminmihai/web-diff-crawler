#!/usr/bin/env bash

#                 Table "public.configurations"
#        Column       |           Type           | Nullable |
# --------------------+--------------------------+----------+
#  runmode            | integer                  |          |
#  dailyschedulebegin | timestamp with time zone |          |
#  dailyscheduleend   | timestamp with time zone |          |
#  id_configurations  | integer                  | not null |
# Indexes:
#     "configurations_pkey" PRIMARY KEY, btree (id_configurations)


#                 Table "public.crawlingrules"
#       Column      |           Type           | Nullable |
# ------------------+--------------------------+----------+
#  id_crawlingrules | integer                  | not null |
#  address          | text                     |          |
#  selectionrule    | text                     |          |
#  lastmodifytime   | timestamp with time zone |          |
#  contributor      | text                     |          |
#  content          | text                     |          |
#  description      | text                     |          |
#  lastcrawltime    | timestamp with time zone |          |
#  crawlperiod      | integer                  | not null |
#  docslinks        | text                     |          |
# Indexes:
#     "crawlingrules_pkey" PRIMARY KEY, btree (id_crawlingrules)


#                  Table "public.notifications"
#            Column           |           Type           | Nullable |
# ----------------------------+--------------------------+----------+
#  id_notifications           | integer                  | not null |
#  address                    | text                     | not null |
#  id_matchingrule            | integer                  |          |
#  modifytime                 | timestamp with time zone |          |
#  currcontent                | text                     |          |
#  oldcontenttime             | timestamp with time zone |          |
#  oldcontent                 | text                     |          |
#  changes                    | text                     | not null |
#  recipients                 | text[]                   |          |
#  ackers                     | text[]                   |          |
#  currdocslinks              | text                     |          |
#  olddocslinks               | text                     |          |
#  coloredcurrcontent         | text                     |          |
#  detectedreplacedorinserted | text                     |          |
#  detecteddeleted            | text                     |          |
#  coloredoldcontent          | text                     |          |
# Indexes:
#     "notifications_pkey" PRIMARY KEY, btree (id_notifications)


#                 Table "public.users"
#     Column     |  Type   | Nullable |                 Default                  
# ---------------+---------+----------+-----------------------------------------+
#  id_users      | integer | not null | nextval('users_id_users_seq'::regclass) |
#  username      | text    |          |                                         |
#  password_hash | text    |          |                                         |
#  secrettoken   | text    |          |                                         |
#  id_roles      | integer |          | 0                                       |
#  email         | text    |          |                                         |
# Indexes:
#     "users_pkey" PRIMARY KEY, btree (id_users)
#     "users_username_key" UNIQUE CONSTRAINT, btree (username)

sudo -u webdiffcrawler -i sh -c '
echo "CREATE TABLE configurations (
runmode INTEGER,
dailyschedulebegin TIMESTAMPTZ,
dailyscheduleend TIMESTAMPTZ,
id_configurations SERIAL PRIMARY KEY);

CREATE TABLE crawlingrules(
id_crawlingrules SERIAL PRIMARY KEY,
address TEXT,
selectionrule TEXT,
lastmodifytime TIMESTAMPTZ,
contributor TEXT,
content TEXT,
description TEXT,
lastcrawltime TIMESTAMPTZ,
crawlperiod INTEGER NOT NULL,
docslinks TEXT);

CREATE TABLE notifications(
id_notifications SERIAL PRIMARY KEY,
address TEXT,
id_matchingrule INTEGER REFERENCES crawlingrules(id_crawlingrules),
modifytime TIMESTAMPTZ,
currcontent TEXT,
oldcontenttime TIMESTAMPTZ,
oldcontent TEXT,
changes TEXT NOT NULL,
recipients TEXT[],
ackers TEXT[],
currdocslinks TEXT,
olddocslinks TEXT,
coloredcurrcontent TEXT,
detectedreplacedorinserted TEXT,
detecteddeleted TEXT,
coloredoldcontent TEXT);

CREATE TABLE users(
id_users SERIAL PRIMARY KEY,
username TEXT UNIQUE,
password_hash TEXT,
secrettoken TEXT,
id_roles INTEGER DEFAULT 0,
email TEXT);

\q" | psql'
