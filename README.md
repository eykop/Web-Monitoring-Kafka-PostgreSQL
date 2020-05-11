# Web monitor using PostgreSQL and Kafka

A simple web monitor solution using PostgreSQL and Kafka, the solution will monitor 
availability of a website through get request, the result of the response will be pushed 
to Kafka through a producer.
The Kafka consumer will consume the results which in turn will be saved in PostgreSQL table.

---

## Run environment and requirement

To be able to run we will need to prepare a working environment with the 
following requirements:

* python 3 
* virtual environment of python 3.
* install required 3rd party libraries used by this solution.
* Kafka server
* PostgreSQL server
* Editing require configuration file.

I will not cover running Kafka and PsotgreSQL server, there are many other totrials
on the internet that cover that.
some are:

* [postgres-kafka-demo](https://github.com/mtpatter/postgres-kafka-demo)
form this one you just need to run the docker compose, the rest is not required.
it will raise Kafka, Zookeeper 
and PostgreSQL server (and some other server not needed by this solution).
* [docker-kafka](https://github.com/spotify/docker-kafka)  
This is and old docker for Kafka server and Zookeeper, but still works.
We will still need a postgreSQL server if we go with seond option that 
can be achieved by the running the following command:

```
docker run -d -p 5432:5432 --name my-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres
```

---

## Python Virtual Environment

We will assume that we already have Python3 installed, if not python can be downloaded 
and installed from https://www.python.org . 
In order to keep our python installation clean and allow ourselves to work with different projects and requirements 
it is recommend that we use a virtual python environment instead of our main python installation.

To create a virtual environment: we will open a terminal and run the following commands:
```
python3 -m venv aiven
source aiven/bin/activate
pip3 install -U pip
```

If we are running on RedHat, CentOS or fedora linux we need to install the PostgreSQL development library
```
sudo dnf install libpq-devel
```
For Debian or ubuntu based distributions we run the following command:
```
sudo apt-get install libpq-dev
```

Finally we install solution requirements
```
pip3 install -r requirements.txt
```

---

## PostgreSQL Database and Table creation

Before we run, we need to create the database and the database table for the Web monitor to be able to
write entries to.

If we have selected to runa PostgreSQL docker container we log to it by the following command:
```
docker exec -it my-postgres "/bin/bash"
``` 
Once we are in the docker bash , we login to the psotgresql console:
```
psql -U postgres
```

We run the following set fo command to create our database and tabel:
```
CREATE DATABASE web_monitor_db;

\connect web_monitor_db;

CREATE TABLE web_check (
                request_id SERIAL PRIMARY KEY,
                url VARCHAR(255) NOT NULL,
                status_code NUMERIC ,
                status_ok boolean NOT NULL,
                response_time NUMERIC ,
                check_metHod VARCHAR(15) NOT NULL,
                pattern_matched boolean NOT NULL,
                requested_pattern VARCHAR(255) NOT NULL,
                matched_text VARCHAR(255) NOT NULL);
```

To check the table creation, we run the following command (still within the container sql console):
```
psql#>\dt

          List of relations
 Schema |   Name    | Type  |  Owner
--------+-----------+-------+----------
 public | web_check | table | postgres
(1 row)


psql#>\d web_check

                                             Table "public.web_check"
      Column       |          Type          | Collation | Nullable |                    Default 
-------------------+------------------------+-----------+----------+-----------------------------------------------
 request_id        | integer                |           | not null | nextval('web_check_request_id_seq'::regclass)
 url               | character varying(255) |           | not null | 
 status_code       | numeric                |           |          | 
 status_ok         | boolean                |           | not null | 
 response_time     | numeric                |           |          | 
 check_method      | character varying(15)  |           | not null | 
 pattern_matched   | boolean                |           | not null | 
 requested_pattern | character varying(255) |           | not null | 
 matched_text      | character varying(255) |           | not null | 
Indexes:
    "web_check_pkey" PRIMARY KEY, btree (request_id)
```

---

## Configuration file
There are several option in the configuration file, it will make our life easier than passing endless command line 
arguments - please note here - the sections and keys names are case sensitives and should not be changed otherwise 
when we run nothing will work.

Mainly there are three section in the configuration.ini file.

#### The firs section is the PosgreSQL configuration, example:

```
[postgresql]
host=192.168.99.100
database=web_monitor_db
user=postgres
password=mysecretpassword
table_name=web_check
```
Note here the database and the table_name are the names we just created in the PostgreSQL section above, 
if you provided different database and table names make sure you update the values in this section. 
**We might need to change the user name and password accordingly to match our server.**


#### The second section is the Kafka server section:

```
[kafka]
host=192.168.99.100:9092
topic=web_checking
bulk_count=1000
group_id=db_writer
```
1. The host of course is the Kafka server address with its port.
2. The topic is the one we will use - depending on your Kafka settings you might need to create the topic, this 
demo assumes it is already created or that the Kafka has auto create topic configuration enabled.
3. The bulk_count key - is how many web check results we accumulate before we flush the Kafka producer buffer 
(for testing purpuse it might be better to set this to a small number of 10 or 5 results).
4. The group_id key is the Kfaka consumer group our consumer will join, this is important since we don't 
want our consumer to keep reading the same messages and insert duplicated entries to the database evrytime it 
restarts or every it a new consumer(that does the same job) subscribe to our topic.
 
**kafka server please note this solution does not handle Kafka authentication (for example user and password)
this might be add in the future or your contribution is welcomed.**


#### The third and final configuration section is the Web Monitor section:
 
```
[web_monitor]
url=http://www.yahoo.com
http_request_type=get
http_success_status_code=200
regex_to_verify=(yahoo).+
monitor_interval_in_sec=3
```

Here we provide the web monitor several options, so it can be used with to monitor different website without the need
 to modify the code.

1. url and http_success_status_code are self explained.
2. monitor_interval_in_sec: is the interval we wait between every check for the url.
3. http_request_type: is the http method we call on the url.
4. regex_to_verify: is a regular expression patter that we will check if it is contained in the web check response we 
get, when regex_to_verify value is empty no check will be done.


## Run the Web Monitor
open a terminal and cd to web_monitor repository folder
To run the producer :
```
python -m scripts.producer -c ./configuration.ini
```
open an other terminal and cd to web_monitor repository folder
To run the consumer :
```
python -m scripts.consumer -c ./configuration.ini
```

## Tests:
There some some unittests for each one of the components, they are regular python unit tests and can be run easily.

## Future Improvements:
* Authentication with Kafka.
* Better SQL tables (separate static ad dynamic data between 2 tables.)
* Better allow Post, Delete, Options web methods for monitoring.
* Improve Partitions and Groups for Kafka Clients.
* Provide script that query the database web monitoring results.
* Add some more unittests.
* Use Kafka Connectors(using Debezium) to sink results directly into the database. 


## Acknowledgments
1. Maria Patterson for her excellent article on 
[Data Stream Processing for Newbies with Kafka, KSQL, and Postgres](https://medium.com/high-alpha/data-stream-processing-for-newbies-with-kafka-ksql-and-postgres-c30309cfaaf8) and mainly her docker compose
2. postgresqltutorial for [postgresql-python tutorial](https://www.postgresqltutorial.com/postgresql-python/)
3. Lorenz Vanthillo for his excellent article on [PostgreSQL and Docker](https://medium.com/better-programming/connect-from-local-machine-to-postgresql-docker-container-f785f00461a7)

