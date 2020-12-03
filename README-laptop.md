Web and phone app for people to post companies that they don't like, to give reasons, for other people to comment and up or downvote companies.

will add more to this later, just reminders on how and where this is being developed.  This development is being started from a copy of dafuckisthat, not all the features below may be implemented yet at the time you read this, and some of the devops stuff might be different - hopefully this documentation will be updated.

The flask server is running on linode.  The IP address is 173.255.247.69.  To start the flask server SSH in and "source activate" from in the /suckycompanies/flask-env/bin directory to start the virtual environment.  Then python3 suckycompanies-api.py in the suckycompanies-api directory.

The react can run locally in suckycompanies/frontend.  npm start to start that, but it also running on the linode server.

the database is on linode mariadb/mysql.  You have to be root to log in.  All pwords are u....w/suffix

All of this is running on its own on the linode server.  It should also be able to run here on the laptop.
in the frontend still do the npm start
start the mysql server with mysqld command
in the backend folder go into the suckycompaniesenv and Scripts and just 'activate' and then back and 'python suckycompanies.py' and then in works more or less

I'm going to use Auth0 I think and already have an account there under jay.new...https://auth0.com/blog/react-tutorial-building-and-securing-your-first-app/ has instructions I'm following

should also look at this (maybe first) for securing the api
https://auth0.com/docs/quickstart/backend/python/01-authorization

auth0, suckycompanies-api, https://173.255.247.69/suckycompanies
public key in JSON Web Key Set format
RS256 algorithm

Not sure about some of the above.  The dev and production environments are completely separate with dev on the laptop.

DEV
npm start from the frontend directory

to start the backend go into backend/suckycompanies/Scripts and do "source activate"
and then back to backend and "python suckycompanies-api.py" to start the serverw

the database is mariadb/mysql.  You have to be root to log in.  All pwords are u....w/suffix
creation of the web user for the db
"CREATE user 'suckycompanies'@'localhost' IDENTIFIED BY 'bgesaw#4'"
"GRANT ALL PRIVILEGES ON suckycompanies.* TO 'suckycompanies'@'localhost'"
"flush privileges"
*(this asterisk just stops italics that started for some reason in vim)

create user mysql
CREATE table user (user_id int not null auto_increment, username varchar(100) not null unique, password_hash varchar(128) not null, sessionvalue varchar(40) default null, primary key(user_id))

create table company (company_id int not null auto_increment, name varchar(100) not null, primary key(company_id))
