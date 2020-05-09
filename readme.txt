To eb able to run you will need to prepare a working environment with ethe following requirements:

1. python 3 
2. virtual environment of python 3.
3. install required 3rd party libraries used by this solution.


I will assume you already have python3 installed, if not python can be downloaded and installed from www.python.org
to keep you python installation clean and allow you to work with different projects and requirements it is recommend that you use
a virtual python environment instead of your main python installation.
to create a virtual environment please open a terminal and run the following commands:

$ python3 -m venv aiven
$ source aiven/bin/activate
$ pip3 install -U pip
$ cd aiven_home_assignement

if you are on fedora linux you need ot install the Postgres development library
$ sudo dnf install libpq-devel
or if your in debian/ubuntu run the following command:
$ sudo apt-get install libpq-dev

finally install requirements
$ pip3 install -r requirements.txt


