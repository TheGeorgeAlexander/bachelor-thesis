# Bachelor Thesis
This is the code and data from my bachelor thesis. Look at [Database Dumps](#database-dumps) if you just want access to the final data. Look at [How To Use](#how-to-use) if you want to run the scripts and create the data yourself.


## Database Dumps

If you want to import the data into a database instead of running the scripts yourself, you can download a database dump and restore the data into your own database. Both the filtered and unfiltered databases are available. You can download a compressed dump from the following links. (Files were too big to be in the repository on GitHub.)
- Unfiltered: https://files.george-alexander.dev/vulnurl.dump (~314 MB)
- Filtered: https://files.george-alexander.dev/vulnurl_filtered.dump (~109 MB)

After you have downloaded a dump, you can restore the database with the following steps.

1. Create a new database: `sudo -u postgres createdb YOUR_DB_NAME`
2. Restore the data from the `vulnurl.dump` dump: `sudo -u postgres pg_restore -d YOUR_DB_NAME vulnurl.dump`

In step 2 you can replace `vulnurl.dump` with `vulnurl_filtered.dump` if you want the filtered data.



## How To Use

This was only tested and used on Linux, not other operating systems. It is assumed all these commands are executed with the current working directory at the root of this project.


### Set up Python environment

1. Create the environment: `python3 -m venv venv`
2. Activate environment: `source venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`


### Set up databases

1. Create the user: `sudo -u postgres createuser vulnurl`
2. Create the databases:
    1. `sudo -u postgres createdb -O vulnurl vulnurl`
    2. `sudo -u postgres createdb -O vulnurl vulnurl_filtered`
3. Initialize databases with the schema and correct `vulnurl` user privileges:
    1. `sudo -u postgres psql -d vulnurl -f init_db.sql`
    2. `sudo -u postgres psql -d vulnurl_filtered -f init_db.sql`


### Run the scripts
It is assumed you have set up [MoreFixes](https://github.com/JafarAkhondali/Morefixes), or your own source database, locally in PostgreSQL. Edit the database name or user that is used for that connection at the top of `src/main.py` if necessary, `SRC_DB_NAME` and `SRC_DB_USER`.

1. Run the main script to fill the `vulnurl` unfiltered database: `python3 src/main.py`
2. Wait until that script is finished. On a strong laptop it took ~20 mins.
3. Run the filtering script to fill the `vulnurl_filtered` database: `python3 src/filter.py`
4. Wait until that script is finished. On a strong laptop it took <1 min.
5. Done!
