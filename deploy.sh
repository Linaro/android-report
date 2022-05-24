#!/bin/bash -ex

if [ -n "$1" ]; then
    work_root=$1
fi
if [ -d "${work_root}" ]; then
    work_root=$(cd ${work_root}; pwd)
else
    echo "Please set the path for work_root"
    exit 1
fi

runserver=${2:-true}

instance_name="android-report"
instance_report_app="report"
instance_dir="${work_root}/${instance_name}"

if ! which sudo; then
    # try to install the sudo package if it's not installed by default
    # as the following steps need to run with sudo
    apt-get update && apt-get install -y sudo
fi

sudo apt-get update
## dependency for python-ldap
sudo apt-get install -y wget curl libsasl2-dev python-dev python3-dev libldap2-dev libssl-dev gcc libjpeg-dev libpq-dev
#sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev tcl8.6-dev tk8.6-dev python-tk
# install for apache and wsgi packages
sudo apt-get install -y python3-pip apache2 libapache2-mod-wsgi-py3

virenv_dir="${work_root}/workspace-python3"
mkdir -p ${virenv_dir}
cd ${virenv_dir}
# https://pip.pypa.io/en/latest/installing/#installing-with-get-pip-py
if [ ! -f get-pip.py ]; then
   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
fi
sudo python3 get-pip.py

# https://virtualenv.pypa.io/en/stable/
sudo pip install virtualenv
virtualenv --python=python3 ${virenv_dir}
source ${virenv_dir}/bin/activate

#(ENV)$ deactivate
#$ rm -r /path/to/ENV

#python manage.py startapp ${instance_report_app}
# django-admin startproject ${instance_name}
cd ${work_root}
if [ -d ${instance_dir} ]; then
    cd ${instance_dir} && git pull && cd -
else
    git clone https://github.com/Linaro/android-report.git ${instance_dir}
fi

# https://docs.djangoproject.com/en/1.11/topics/install/#installing-official-release
# https://django-debug-toolbar.readthedocs.io/en/latest/changes.html
pip install -r ${instance_dir}/requirements.txt
#pip install Django==3.0.8
# https://django-auth-ldap.readthedocs.io/en/latest/install.html
#pip install django-auth-ldap # needs python-ldap >= 3.0
#pip install bugzilla
## pip install Pillow
## pip install rst2pdf

# https://docs.djangoproject.com/en/1.11/intro/tutorial01/
python3 -m django --version

if ! grep -q SECRET_KEY ${instance_dir}/lcr/settings.py; then
    if [ ! -v SECRET_KEY ]; then
        SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    fi
    echo "SECRET_KEY = '${SECRET_KEY}'" >> ${instance_dir}/lcr/settings.py
fi

cd ${instance_dir}
mkdir -p datafiles/logfiles/
sudo chown -R :www-data datafiles
sudo chmod 775 datafiles
sudo chmod 775 datafiles/logfiles
if [ -n "$(ls -A datafiles/logfiles)" ]; then
    sudo chmod 664 datafiles/logfiles/*
    sudo chown ${USER}: datafiles/logfiles/*
fi
rm -fr datafiles/db.sqlite3
python3 manage.py migrate
# for apache admin display
if grep DEPLOYED_WITH_APACHE ${instance_dir}/lcr/settings.py |grep -i "true"; then
    yes 'yes' | python3 manage.py collectstatic || true
fi
python3 manage.py createsuperuser --username admin --email example@example.com --noinput
if [ -z "${runserver}" ] || [ "${runserver}" != "false" ]; then
    echo "Please access the site via http://127.0.0.1:8000/lkft"
    echo "And you still need to update the bugzilla, qa-report tokens to resubmit job or create bugs"
    python3 manage.py runserver 0.0.0.0:8000
fi

# python  manage.py collectstatic
# By running makemigrations, you’re telling Django that you’ve made some changes to your models (in this case,
# you’ve made new ones) and that you’d like the changes to be stored as a migration.
# python manage.py makemigrations report

# The migrate command looks at the INSTALLED_APPS setting and creates any necessary database tables according to the database settings
# in your mysite/settings.py file and the database migrations shipped with the app (we’ll cover those later)
# Need to run after makemigrations so that the tables for report could be created
# python manage.py migrate

# There’s a command that will run the migrations for you and manage your database schema automatically - that’s called migrate,
# and we’ll come to it in a moment - but first, let’s see what SQL that migration would run.
# The sqlmigrate command takes migration names and returns their SQL:
# Only shows the sql script, not creation
# python manage.py sqlmigrate report 0002

# cp db.sqlite3 db.sqlite3.bak.$(date +%Y%m%d-%H%M%S)
# scp android:/android/django_instances/lcr-report/db.sqlite3 ./
# cat jobs.txt |awk '{print $2}' >job-ids.txt
# sqlite3 db.sqlite3 "select * from report_testcase where job_id = 99965 ORDER BY name;"
# sqlite3 db.sqlite3 "delete from report_testcase where job_id = 99859;"
# https://www.sqlite.org/lang.html
# https://www.sqlitetutorial.net/sqlite-index/
#   CREATE [UNIQUE] INDEX index_name ON table_name(column_list);
#   CREATE INDEX idx_contacts_name ON contacts (first_name, last_name);
#   PRAGMA index_list('table_name');
#   PRAGMA index_info('index_name');
#   DROP INDEX [IF EXISTS] index_name;
#   EXPLAIN QUERY PLAN sql_sentence


## with new db.sqlite3 file
## 1. remove the reference for the app in the lcr/urls.py
## 2. run python manage.py migrate to generate a new database
## 3. python manage.py createsuperuser to create a new user
## 4. setup build configs, lava uses from the admin ui
## 5. restartwith python manage.py runserver 0.0.0.0:9000

## AttributeError: module 'yaml' has no attribute 'CLoader'
# https://pyyaml.org/wiki/PyYAMLDocumentation
# $ wget -c http://pyyaml.org/download/libyaml/yaml-0.2.5.tar.gz
# $ tar xvf yaml-0.2.5.tar.gz
# $ cd yaml-0.2.5/
# $ ./configure
# $ make
# $ sudo make instal
# $ wget -c http://pyyaml.org/download/pyyaml/PyYAML-5.3.1.tar.gz
# $ tar xvf PyYAML-5.3.1.tar.gz
# $ cd PyYAML-5.3.1/
# $ python setup.py --with-libyaml install
