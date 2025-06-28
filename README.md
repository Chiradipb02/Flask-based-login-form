# Basic Login Signup Form using Flask and MySQL
## Goals:--
* Homepage will show login and register option to the user
* If user has not registered he has to register [give name, password, email]. Make sure 1 email->1 account.
* The user can make account only 1x with 1 email and use it thereafter. So a database has to be maintained.
* The dashboard can show the user name mail etc. Contain a logout button
* The login page [if logout pressed should flash successfully logged out] should have mail and password entry. Query the mail in database if found match the password. Otherwise flash message incorrect mail/password 
* Each of the login and register page should have button for the other "if yes/not then".
* The password of the user should not be stolen, so hash it

## Steps taken
1. Make the basic skeleton of the website by making routes for homepage, login, register, dashboard [also the webpages using html]
2. Jinja can be used to extend the common layout of each page by writing it in one layout.html and distributing. Leaving block content for each page for their unique stuff.
3. Make the form using WT-FORM
4. Create a database in phpmyadmin then use it via mysql.
5. Each time the register is pressed add a new entry to database, primary key=id
6. For login for each press the database is queried to find email and then match the password.
