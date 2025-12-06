
### Install redis
---
- docker run --name some-redis -p 6379:6379 -d redis
- everything else is configured in base/settings.py

### Install MySQL 
---
- docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=root-pw -d mysql

### Install phpmyadmin and configure mysql using it
---
- docker run --name phpmyadmin -d --link some-mysql:db -p 8080:80 phpmyadmin
- in browser go to: http://localhost:8080/
- Username: root
- Password: root-pw
- Go for User accounts tab at the top
- Click Add user account
- Fill:
    - User name: sport-complex-cw
    - Password: sport-complex-cw
    - Check: Create database with same name and grant all privileges.
    - Press Go at the bottom

### Install CouchDB
---
- docker run --name some-couchdb -e 'COUCHDB_USER=couchdb' -e 'COUCHDB_PASSWORD=couchdb' -p 5984:5984 -d couchdb
- everything else configured in settigns.py and core

### Install Neo4j
---
- docker run --name some-neo4j -p 7474:7474 -p 7687:7687 -d neo4j
- go in browser for: http://localhost:7474/
- Connect: Username: neo4j | Password: neo4j
- Set the new password to: neo4jneo4j
- everything else configured in settigns.py and core


### RUN
---
/Course-work-sport-complex-fa$ python main.py 
/Course-work-sport-complex-fa/frontend$ npm run dev