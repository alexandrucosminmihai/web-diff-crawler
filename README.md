# webDiffCrawler
## Note: this readme is outdated. A new one is coming soon.
#### The core is the same, but some structure details have changed
*webDiffCrawler* is a crawler that is meant to periodically check webpages or elements of webpages as instructed by entries in a *crawling rules* database table and generate notifications when it finds any difference between the old known version of the webpage/element and the newly scraped one.

*webDiffCrawler* is based on the [Scrapy framework](https://docs.scrapy.org/en/latest/index.html) and, for the implementation in this repository, at the moment, it uses a [PostgreSQL](https://www.postgresql.org/) database and [SQLAlchemy](https://www.sqlalchemy.org/) to communicate with it, but it can be easily changed to work with any database system accepted by SQLAlchemy.

## Basic installation steps
###### (might not be complete and/or fully descriptive)
1. First of all, make sure you have `python3` on the system and install the dependencies:
    - related to your database system
    - `pip3 install sqlalchemy`
    - `pip3 install scrapy`
    - `pip3 install scrapyd`
    - `pip3 install scrapyd-client`

2. Set up your database system if not already done (see below for a PostgreSQL example);
3. Clone the Scrapy project from this repository;
4. Modify the SQLAlchemy engine database URL in `webDiffCrawler.py` in order to match you database system and authentification credentials;
5. Create a table in your database named `crawlingrules` with the following header:
    ```
     Column          |           Type           |
    -----------------+--------------------------+
    id_crawlingrules | integer (the primary key)|
    address          | text (a webpage url)     |
    selectionrule    | text (a css selector)    |
    lastmodifytime   | timestamp with time zone |
    contributor      | text                     |
    content          | text                     |
    ```
    and populate it with the `crawlingrules` you want the crawler to follow.
    - e.g.:
        ```
        id_crwalingrules = 4
        address = https://time.is
        selectionrule = #twd::text 
        lastmodifytime = 2018-12-20 20:00:07.586726+02
        contributor = testUser
        content = 20:00:07
        ```
6. Create a table in your database named `notifications` with the following header:
    ```
        Column           |           Type           |
        -----------------+--------------------------+
        id_notifications | integer (the primary key)|
        address          | text (scraped page URL)  | 
        matchingrule     | text (matched selector)  | 
        modifytime       | timestamp with time zone |
        content          | text (diff content)      |
        recipients       | text[]                   |
        ackers           | text[]                   |
    ```
7. Go to the project's location and start the Scrapy daemon: `scrapyd` ;
8. Deploy the current Scrapy project with its spider `scrapyd-deploy` ;
9. Add a `cron` job that schedules periodic spider crawling jobs:
    - `crontab -e`
    - add the following line to the file: 
    ```
    0 * * * * curl http://localhost:6800/schedule.json -d project=webDiffCrawler -d spider=webDiffCrawler
    ```
    This line issues crawling jobs to scrapyd every hour. You can check this [link](https://corenominal.org/2016/05/12/howto-setup-a-crontab-file/) to see how to modify the time period.

## Miscellaneous
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

