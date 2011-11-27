For convenience, create a virtual environment.  Install the necessary dependencies
into this environment and create a symlink to its Python executable.

::

    $ cd ~/pythonenv
    $ virtualenv --no-site-packages RETSQUERY
    $ RETSQUERY/bin/pip install mox lxml
    $ cd ~/bin
    $ ln -s /home/<user>/pythonenv/RETSQUERY/bin/python retsquery-python

To run unit tests::

    $ retsquery-python -m unittest discover -s test -v
    
    Execute this command from the root directory of the project, as this sets
    the working directory.
    
To run the sample application, you must have access to RETS server.  Create an
example/settings.ini from based on example/settings.ini.sample and populate it
with your own values.

Run the example application::

    $ retsquery-python example/client.py