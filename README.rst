===============
Heroku Tutorial
===============

A tutorial demonstrating a simple Python web application written with the
Flask microframework. The tutorial contains several snapshots which show
new components incrementally added to the application. These snapshots are
marked by release tags. The components demonstrated are:

 - Amazon S3
 - Postgres
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

   git clone https://github.com/sprin/heroku-tut.git
   cd heroku-tut
   git fetch --tags


In the Heroku UI, start a new app and give it a name. Use the format
``{{your_handle}}-htut``, eg. ``sprin-htut``.

In your local repo, add the newly-created Heroku repo as a remote:

.. code::

   git remote add heroku git@heroku.com:{{your_handle}}-htut.git

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
---------------

"Hello from..." - oops.
Let's see where that is coming from and fix it.

Ah, it's coming from an environment variable. Environment variables are
how you configure apps. Heroku calls them config vars. Let's set the
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

Let's provision a database via the command line:

.. code::

   heroku addons:add heroku-postgresql:dev

This will set up a database and print the config var which holds the connection
string. Heroku assumes you may want to configure more than one database per
app, but if not, you can change the config var to simply ``DATABASE_URL``. So
if the printed connection string is ``HEROKU_POSTGRESQL_ORANGE_URL``, we can
do:

.. code::

   heroku pg:promote HEROKU_POSTGRESQL_ORANGE_URL

Run a One-off Dyno
------------------

Now let's check out and push the tag which will read those config vars:

.. code::

  git checkout 0.3.0-postgres
  git push heroku 0.3.0-postgres^{}:master

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

In this tag, there's a new view which tests the connection to the Postgres
database by inserting a fake record into a table, and returns the result as
JSON at ``http://{{your_handle}}-htut.herokuapp.com/test_connection``.

.. unicorns unicorns unicorns moar unicorns

Now for some fun
----------------

Upload a file and look for a new link in the success message.

Submodules
----------

This new tag introduced a submodule... an external git repository referenced
from our repository. Heroku fetches any submodules contained within the pushed
repository, so that you can use code from submodules without having to copy
their code into your repository. Submodules also allow for easy
updating of the external repo's code. However, a production setup
should probably keep a cloned repo around which application repos can
reference, rather than the external repo itself. This protects against
the breakage or unavailability of the external repo.

CloudAMQP
---------

CloudAMQP is a hosted RabbitMQ service. RabbitMQ is a message queueing
framework which allows us to create jobs to be processed asynchronously.
Rather than tying up a web process to do heavy-lifting, we can offload the
work to another process, called a worker. Perhaps more importantly for large
applications, queuing allows an application to be decomposed into many
independent pieces - they can even be written in different languages.

If we have a single web process performing the word count, and a large
file is uploaded, we may be unable to serve other requests. So let's offload
the word count to a worker process. First, let's provision the RabbitMQ
service:

.. code::

   heroku addons:add cloudamqp


Now let's deploy the new tag and scale our app up with a worker:

.. code::

   git checkout 0.4.0-queuing
   git push heroku 0.4.0-queuing^{}:master
   heroku ps:scale worker=1

We can watch the worker in action by tailing the Heroku logs:

.. code::

   heroku logs --tail

From the user's perspective, our app can now return a response much faster for
large uploads, and we are less likely to have availability problems due to
overloaded web processes. There's a chance that the user clicks the word cloud
link before the word count has been completed, but situations like this can be
handled with Javascript that can show the link, or redirect the user, when
informed of the job finishing. The Javascript client can communicate with the
server via server-sent events, or fall back to polling for older browsers. But
clever Javascript solutions are outside the scope of this tutorial, and left as
an exercise for the reader ;)

Summary
=======

Awesome! You can now:

 - Provision and deploy to a production platform
 - Use Amazon S3 for file storage
 - Configure add-on services, such as Postgres and RabbitMQ
 - Scale your application using additional web and worker processes

