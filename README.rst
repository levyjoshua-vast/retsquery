Install the necessary Python dependencies::

    $ sudo pip install mox lxml

To run unit tests::

    # From the project root directory
    $ python -m unittest discover -s test/ -v
    
To run the sample application, you must have access to RETS server.  Create an
example/settings.ini from based on example/settings.ini.sample and populate it
with your own values.

Run the example application::

    $ python example/client.py
    