===============
Heroku Tutorial
===============

A tutorial demonstrating a simple Python web application written with the
Flask microframework. The tutorial contains several snapshots which show
new components incrementally added to the application. These snapshots are
marked by release tags. The components demonstrated are:

 - Amazon S3
 - Heroku Postgres
 - CloudAMPQ

The final application will take a file upload, store the file on S3,
process the contents asynchronously, and insert the result into the
database.

To make this somewhat interesting, the application will generate a word
frequency count and returns the result to the client. The client then
renders it into a word cloud using the `d3-cloud`_ library by Jason Davies.
Word counts will be stored in the database for later retrieval at a URL
specified by the name the user gives to the file upload.

.. _d3-cloud: https://github.com/jasondavies/d3-cloud

