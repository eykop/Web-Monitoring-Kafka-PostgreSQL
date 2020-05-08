To eb able to run you will need to prepare a working envinrment with ethe following reuiqrements:

1. python 3 
2. virtual envrinment of python 3.
3. install required 3rd party libraries used by this solution.


I will assume you already have python3 installed, if not python can be downlaoded and installed from www.python.org
to keep you python installation clean and allow you to work with different projects and reuqirments it is recommend that you use 
a vritual python envinrment instead of your main python installtion.
to create a virtual envirnment please open a terminal and run the following commands:

$ python3 -m venv aiven
$ cd aiven_home_assignement
$ source aiven/bin/activate 
$ pip3 install -U pip

if you are on fedora linux you need ot install thePostgres development library
$ sudo dnf install libpq-devel
or if your in debian/ubuntu run the following ocmmand:
$ sudo apt-get install libpq-dev

$ pip3 install -r requirements.txt


