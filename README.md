# Metric Collector Assignment


### Prerequisites
 
Before running this project, assume that :
1. You already have an account on [Aiven](https://console.aiven.io/)
2. You have created a **Kafka** service running on Aiven and added a kafka topic (you can do it easily on the Aiven web console).
3. You have created a **PostgreSQL** service running on Aiven (you can do it easily on the Aiven web console).
4. You have [Docker](https://docs.docker.com/get-docker/) installed on your machine.
5. You have [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.

### Project structure

    │── db_scripts                                # database setup
    │   │── db_setup.sh                           # script for setting up
    │   │── Dockerfile                            # Docker file to build db script image
    │   │── functions.sql                         # sql function for the project
    │   │── schemas.py                            # schema creation sql 
    
    │── metrics                                   # metric package
    │   │── collector                             # collector package
    │   │     │── __init__.py                      
    │   │     │── collector.py                    # collector module code
    │   │── model                                 # model package for db request
    │   │     │── __init__.py                      
    │   │     │── db.py                           # db base class 
    │   │     │── metric_db.py                    # metric db class inherited of db
    │   │── persistor                             # persistor module
    │   │     │── __init__.py                     
    │   │     │── persistor.py                    # kafka consummer and db writter
    │   │── request                               # package for db http request
    │   │     │── __init__.py                      
    │   │     │── http_request.py                 # http request call module 
    │   │── utils                                 # utilities 
    │   │     │── __init__.py                      
    │   │     │── constants.py                    # constants of the project
    │   │     │── helpers.py                      # helper function (log, kafka producer, etc..)
    
    │── test                                      # test folder
    │   │── __init__.py                
    │   │── test_collector.py                     # collector unit test
    │   │── test_persistor.py                     # persistor unit test
    
    │── .env.example.yml                          #  env example file 
    │── docker-compose.yml                        #  compose file for running the project
    │── Dockerfile                                #  Docker deployment file
    │── main.py                                   #  main code for launching ptoject
    │── requirements.txt                          #  python requirement.txt file
    │── test.yml                                  #  compose file for test
    └── ...

## Running The Project

#### 1. Setup the database 

   ```sh
 docker run -e METRIC_DB_URL=postgres://<username>:<password>@<host>:<port>/<database>?sslmode=require -d florentio/aiven_hw_db_setup bash /home/script/db_setup.sh
   ```

Please, set **METRIC_DB_URL** with the PostsgreSQL service URI of your Aiven service, you can find it in the detail of your service on Aiven console.

#### 2. Configure the project
  Before running the project you will need to define some environment variable for  Kafka, PostgreSQL connection  and certificate for Kafka connection.
  
 - Clone or download the project
 - Create a folder `certs` in the root path of the project
 - Download your **Access Key**, **Access Certificate** and **CA Certificate** from your Aiven Kafka service page into the `certs` folder.
 - Create your `.env` file in the root of your project based on `.env.example` and update your key/value pairs in the following format of `KEY=VALUE`
	 
    ```sh
   KAFKA_BOOTSTRAP_SERVER=kafka-xxxxxxx.aivencloud.com:XXXX 
   KAFKA_TOPIC=my_topic  
   METRIC_DB_URL=postgres://<username>:<password>@<host>:<port>/<database>?sslmode=require  
   WEBSITES=https://github.com|github;https://example.com|  
   METRIC_COLLECTOR_FREQ=20
   ```
   
Read    `.env.example` to know more about the value for each parameter

#### 3. Run tests
 
 ```sh
 docker-compose -f test.yml up -d
   ```

#### 4. Run the project
 
 ```sh
 docker-compose up -d
   ```


#### 5. Optimization
- Collect all logs into tools like ElasticSearch for analysis 
- Metric Data visualization (read data from the DB and display them)


#### 6. Credits
Florentio DE SOUZA 
