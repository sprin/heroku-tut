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

Let's begin
===========

Deploy your first app
---------------------

Clone the tutorial repo and fetch all the tags:

.. code:: bash

   git clone git@github.com:sprin/heroku-tut.git
   git fetch --tags

In the Heroku UI, start a new app and give it a name. Use the format
``{{your_handle}}-htut``, eg. ``sprin-htut``.

In your local repo, add the newly-created Heroku repo as a remote:

.. code:: bash

   git remote add heroku git@heroku.com:sprin-htut.git

Push the first tag to Heroku to deploy!

.. code:: bash

   git push heroku 0.1.0-hello-world

Watch as Heroku herds green unicorns and such.

Visit your app at ``http://{{your-handle}}-htut.herokuapp.com``.

Setting Config Vars
-------------------

"Hello from..." - oops.
Let's see where that is coming from and fix it.

Ah, it's coming from an environment variable. Environment variables are
how you configure Heroku apps. Heroku calls them config vars. Let's set the
``ME`` config var to your handle.

.. code:: bash

   heroku config:set ME=sprin

