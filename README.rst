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

.. code::

   git clone git@github.com:sprin/heroku-tut.git
   git fetch --tags


In the Heroku UI, start a new app and give it a name. Use the format
``{{your_handle}}-htut``, eg. ``sprin-htut``.

In your local repo, add the newly-created Heroku repo as a remote:

.. code::

   git remote add heroku git@heroku.com:sprin-htut.git

Push the first tag to Heroku to deploy!

.. code::

   git push heroku 0.1.0-hello-world^{}:master

Heroku only deploys code from pushes to it's master branch. However, above,
we push a local tag to Heroku's master branch.

Watch as Heroku herds green unicorns and such.

Visit your app at ``http://{{your_handle}}-htut.herokuapp.com``.

Let's take a look at that tag:

.. code::

  git checkout 0.1.0-hello-world

Set config vars
-------------------

"Hello from..." - oops.
Let's see where that is coming from and fix it.

Ah, it's coming from an environment variable. Environment variables are
how you configure Heroku apps. Heroku calls them config vars. Let's set the
``ME`` config var to your handle.

.. code::

   heroku config:set ME=sprin

Upload files to S3
------------------

You can't store files on the local filesystem with Heroku instances. If you
want to store files, such as user uploads, you can use Amazon S3.

Assuming you already have an S3 account, create a new bucket called
``{{your_handle}}-htut``. This example uses the Northern California (us-west-1)
region. Make a directory in it called ``files``.

Checkout the next tag:

.. code::

  git checkout 0.2.0-s3-uploads

We need to set the following config vars for S3:


.. code::

   heroku config:set S3_LOCATION=https://s3-us-west-1.amazonaws.com/
   heroku config:set S3_KEY={{your_s3_key}}
   heroku config:set S3_SECRET={{your_s3_secret_key}}
   heroku config:set S3_UPLOAD_DIRECTORY='files'
   heroku config:set S3_BUCKET='{{your_handle}}-htut'

This example uses Flask sessions. To use sessions inside Flask, you need to
set a secret key. It can be any secret, complex, random value.

.. code::

heroku config:set FLASK_SECRET_KEY={{secret_complex_random_value}}

Now let's deploy this tag:

  git push heroku 0.2.0-s3-uploads^{}:master

Create a Postgres Database
--------------------------

Head to  https://postgres.heroku.com/databases to fire up a DB. Launch a
"Dev Plan (free)" database. Once it initializes, get the connection settings.
Note that you can connect instantly with psql by clicking the connection
settings icon, selecting the PSQL option, and pasting the command into a
shell. But we want our application to connect, so let's set some more config
vars!

.. code::

   heroku config:set DB_USER={{your_db_user}}
   heroku config:set DB_PASSWORD={{your_db_password}}
   heroku config:set DB_HOST={{your_db_host}}
   heroku config:set DB_PORT={{your_db_post}}
   heroku config:set DB_NAME={{your_db_name}}

Run a One-off Dyno
------------------

Now let's check out the tag which will read those config vars:

.. code::

  git checkout 0.3.0-postgres

Let's run a "one-off" dyno to create the initial table in Postgres:

.. code::

   heroku run python app/initial_tables.py

Restart the app
---------------

With the tables created, let's restart the app to reflect the new tables.

.. code::

   heroku restart web

Test the connection
-------------------

In this tag, there's a new view which tests the connection by inserting a
fake record into a table, and returns the result as JSON at
``http://{{your_handle}}-htut.herokuapp.com/test_connection``.

.. unicorns unicorns unicorns moar unicorns

