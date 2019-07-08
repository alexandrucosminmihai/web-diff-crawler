# webDiffCrawler

*webDiffCrawler* is a crawler that is meant to periodically check webpages or elements of webpages as instructed by entries in a *crawling rules* database table and generate notifications when it finds any difference between the old known version of the webpage/element and the newly scraped one.

*webDiffCrawler* is based on the [Scrapy framework](https://docs.scrapy.org/en/latest/index.html) and, for the implementation in this repository, at the moment, it uses a [PostgreSQL](https://www.postgresql.org/) database and [SQLAlchemy](https://www.sqlalchemy.org/) to communicate with it, but it can be easily changed to work with any database system accepted by SQLAlchemy.

## Basic installation steps for Ubuntu + Python 3 + PostgreSQL

### Step 1: Set up your database system 
If not already done (see below for a PostgreSQL example) and add the **required tables**:

##### Database tables
On the TODO list is adding migrations, probably using Alembic.

In the meanwhile, the bash script `dbtables_init.sh` will create the tables assuming there is a 
`webdiffcrawler` PostgreSQL role.

You can change the user role to whatever username you are using.

```
./dbtables_init.sh
```

Here are the tables it creates:

```
                Table "public.configurations"
       Column       |           Type           | Nullable |
--------------------+--------------------------+----------+
 runmode            | integer                  |          |
 dailyschedulebegin | timestamp with time zone |          |
 dailyscheduleend   | timestamp with time zone |          |
 id_configurations  | integer                  | not null |
Indexes:
    "configurations_pkey" PRIMARY KEY, btree (id_configurations)

```

```
                Table "public.crawlingrules"
      Column      |           Type           | Nullable |
------------------+--------------------------+----------+
 id_crawlingrules | integer                  | not null |
 address          | text                     |          |
 selectionrule    | text                     |          |
 lastmodifytime   | timestamp with time zone |          |
 contributor      | text                     |          |
 content          | text                     |          |
 description      | text                     |          |
 lastcrawltime    | timestamp with time zone |          |
 crawlperiod      | integer                  | not null |
 docslinks        | text                     |          |
Indexes:
    "crawlingrules_pkey" PRIMARY KEY, btree (id_crawlingrules)
```

```
                 Table "public.notifications"
           Column           |           Type           | Nullable |
----------------------------+--------------------------+----------+
 id_notifications           | integer                  | not null |
 address                    | text                     | not null |
 id_matchingrule            | integer                  |          |
 modifytime                 | timestamp with time zone |          |
 currcontent                | text                     |          |
 oldcontenttime             | timestamp with time zone |          |
 oldcontent                 | text                     |          |
 changes                    | text                     | not null |
 recipients                 | text[]                   |          |
 ackers                     | text[]                   |          |
 currdocslinks              | text                     |          |
 olddocslinks               | text                     |          |
 coloredcurrcontent         | text                     |          |
 detectedreplacedorinserted | text                     |          |
 detecteddeleted            | text                     |          |
 coloredoldcontent          | text                     |          |
Indexes:
    "notifications_pkey" PRIMARY KEY, btree (id_notifications)
```

```
                Table "public.users"
    Column     |  Type   | Nullable |                 Default                  
---------------+---------+----------+-----------------------------------------+
 id_users      | integer | not null | nextval('users_id_users_seq'::regclass) |
 username      | text    |          |                                         |
 password_hash | text    |          |                                         |
 secrettoken   | text    |          |                                         |
 id_roles      | integer |          | 0                                       |
 email         | text    |          |                                         |
Indexes:
    "users_pkey" PRIMARY KEY, btree (id_users)
    "users_username_key" UNIQUE CONSTRAINT, btree (username)
```

### Step 2: Make sure you have the environment variables set :
```
export SECRET_KEY="Change me with something hard to guess"
export DATABASE_URL="postgresql://DB_USER:DB_PASSWORD@localhost/OS_USER" # DB_USER = OS_USER = webdiffcrawler for example
export FLASK_APP=webapp.py # Useful for debugging using the development server, otherwise Flask will look for wsgi.py or app.py
export FLASK_DEBUG=1 # Use it only in development! It can be a security risk
```

You might want to append these export commands to the end of your `venv/bin/activate` script

### Step 3: Install these packages before running pip :

```
sudo apt-get install libcairo2-dev libjpeg8-dev libpango1.0-dev libgif-dev build-essential g++
sudo apt-get install gobject-introspection
sudo apt-get install libgirepository1.0-dev
sudo apt-get install python3-cairo python3-cairo-dev python3-cairo-doc
```

### Step 4: Install the Python packages described in requirements.txt :
```
pip install -r requirements.txt
```

Note: WebDiffCrawler uses `Python 3.6`. If you're having trouble with pip, it might be because it's not actually
using pip3, so try `pip3 install -r requirements.txt`


### Step 5: Modify the SQLAlchemy engine database URL
In `webDiffCrawler/webDiffCrawler/spiders/webDiffCrawler.py` and in `webapp_webDiffCrawler/config.py` in order to match you database system and authentification credentials.

### Step 6: Go to the project's location and start the Scrapy daemon: `scrapyd`

### Step 7: Deploy the current Scrapy project with its spider using `scrapyd-deploy`

### Step 8: Add a `cron` job that schedules periodic spider crawling jobs :

1. `crontab -e`
2. append the following line to the file: 
```
0 * * * * curl http://localhost:6800/schedule.json -d project=webDiffCrawler -d spider=webDiffCrawler
```
This line issues crawling jobs to scrapyd every hour. You can check [this link](https://corenominal.org/2016/05/12/howto-setup-a-crontab-file/) to see how to modify the time period.

## Miscellaneous
### Apache2 deployment using mod_wsgi on Ubuntu
If you are using mod_wsgi to deploy using Apache2 on Ubuntu, beware that `apt-get install libapache2-mod-wsgi`
will install an old, outdated version of mod_wsgi.

You most probably want to install mod_wsgi following:
* Mainly the instructions [here](https://stackoverflow.com/questions/30674644/installing-mod-wsgi-for-python3-on-ubuntu?noredirect=1)
* But [this](https://stackoverflow.com/questions/30674644/installing-mod-wsgi-for-python3-on-ubuntu?noredirect=1) can be useful for more context


### PostgreSQL setup example
1. Install the postgreSQL packages;
2. `sudo -i -u postgres` ;
3. `createuser --interactive` - ident authentication => userX (both as postgresql role and unix user) ;
4. `createdb userX` - by default postgreSQL expects there to be a database with the same name as the user ;
5. `logout`
6. `sudo vim /etc/postgresql/10/main/pg_hba.conf` - we need to set up a password for the postgreSQL(not UNIX) user we've created;
7. Add the following lines and save:
    ```
	local all postgres peer
	local userX userX peer
    ```
8. `sudo service postgresql restart` ;
9. `sudo -i -u userX` ;
10. `psql` ;
11. `ALTER USER userX PASSWORD 'userX_postgreSQL_password';` ;
12. `sudo vim /etc/postgresql/10/main/pg_hba.conf` ; 
13. delete the lines you've written before
14. `sudo service psotgresql restart` .

### Useful `psql` commands
```
* >psql -d dataB 	# current user connects to dataB instead of his default database
* =# \d 		# lists the relations in the current database
* =# \dt		# lists only the tables in the current database, without the sequences
* =# \l 		# lists the databases
* sql instructions; example: 'SELECT * FROM tableName;'
* =# \q			# exit the postgreSQL prompt
* =# \d+ tableName	# lists the columns (header) of the table
```

