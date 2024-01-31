# Install Netbox on Ubuntu 22.04

## Objective

## Procedure

https://docs.netbox.dev/en/stable/installation/

#### postgres database install

1. get into your netbox VM.

    `$` `ssh netbox`

    > Type **yes** if prompted.

0. Update update your apt. 

    `$` `sudo apt update`

0. Install postgresql.

    `$` `sudo apt install -y postgresql`

0. Check your version. Make sure it is at least v12.

    `$` `psql -V`

0. Create the database.

    `$` `sudo -u postgres psql`

    ```
    CREATE DATABASE netbox;
    CREATE USER netbox WITH PASSWORD 'alta3';
    ALTER DATABASE netbox OWNER TO netbox;
    \q
    ```

    > **\q** to quit

    > In postgresql **15** and up, you'll have to add the below two commands to the bottom of the above list before moving forward.

    ```
    \connect netbox;
    GRANT CREATE ON SCHEMA public TO netbox;
    ```

0. Verify authentication to the service. (Don't forget you will have to enter the password you just created).

    `$` `psql --username netbox --password --host localhost netbox`

0. Check on the connection info.

    `netbox=>` `\conninfo`

0. Exit out of the database.

    `netbox=>` `\q`

#### Install redis

1. Apt install redis-server

    `$` `sudo apt install -y redis-server`

0. Check the version of redis and ping to verify functionality. You're looking for v4 or higher.

    `$` `redis-server -v`

    `$` `redis-cli ping`

    ```
    PONG
    ```

#### Actually installing Netbox

1. Install dependencies for Netbox

   `$` `sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential libxml2-dev libxslt1-dev libffi-dev libpq-dev libssl-dev zlib1g-dev`

0. Verify your python version is 3.8 or higher.

    `$` `python3 -V`

0. Set up the file structure for Netbox.

    `$` `sudo mkdir -p /opt/netbox/`

    `$` `cd /opt/netbox/`

0. Clone the repository, getting the latest stable release.

    `$` `sudo git clone -b master --depth 1 https://github.com/netbox-community/netbox.git .`

0. Set up Netbox with a system user and subsequently set permissions.

    `$` `sudo adduser --system --group netbox`

    `$` `sudo chown --recursive netbox /opt/netbox/netbox/media/`

    `$` `sudo chown --recursive netbox /opt/netbox/netbox/reports/`

    `$` `sudo chown --recursive netbox /opt/netbox/netbox/scripts/`

0. Cd into your netbox directory.

    `$` `cd /opt/netbox/netbox/netbox/`

0. Copy the sample configuration script to what you will actually be using it for.

    `$` `sudo cp configuration_example.py configuration.py`

0. Make a secret key, required for Netbox to run.

    `$` `python3 ../generate_secret_key.py`

    > copy that key to your clipboard. You will need it in the next step.

0. Edit the script and adjust the below lines to look as follows

    `$` `sudo vi configuration.py`

    ```python3
    ALLOWED_HOSTS = ['*']         ############## UPDATE allowed_hosts to be any 
    ---
    # PostgreSQL database configuration. See the Django documentation for a complete list of available parameters:
    #   https://docs.djangoproject.com/en/stable/ref/settings/#databases
    DATABASE = {
        'ENGINE': 'django.db.backends.postgresql',  # Database engine
        'NAME': 'netbox',         ############## UPDATE Database name
        'USER': 'netbox',         ############## UPDATE PostgreSQL username
        'PASSWORD': 'alta3',      ############## PostgreSQL password
        'HOST': 'localhost',      # Database server
        'PORT': '',               # Database port (leave blank for default)
        'CONN_MAX_AGE': 300,      # Max database connection age
    }
    ---
    SECRET_KEY = ''              ############## UPDATE with key you made in previous step
    ```
    
0. Now run the upgrade script to actually install Netbox. 

    `$` `sudo /opt/netbox/upgrade.sh`

0. Begin using the virtual environment.

    `$` `source /opt/netbox/venv/bin/activate`

0. Change to the netbox directory if you are not already there.

    `(venv) student@netbox:/opt/netbox/netbox$` `cd /opt/netbox/netbox`

0. Create a superuser for Netbox because there are no inherent user accounts.

    `(venv) student@netbox:/opt/netbox/netbox$` `python3 manage.py createsuperuser`

    > Keep **student** as the user, **alta3** as the password, and press enter when prompted with the email address as it is not required.

0. Make sure your system has a cron job set for daily cleanup.

    `(venv) student@netbox:/opt/netbox/netbox$` `sudo ln -s /opt/netbox/contrib/netbox-housekeeping.sh /etc/cron.daily/netbox-housekeeping`

0. Test the service.

    `(venv) student@netbox:/opt/netbox/netbox$` `python3 manage.py runserver 0.0.0.0:8000 --insecure`

    ```
               Performing system checks...
    
    System check identified no issues (0 silenced).
    January 12, 2024 - 19:19:48
    Django version 4.2.8, using settings 'netbox.settings'
    Starting development server at http://0.0.0.0:8000/
    Quit the server with CONTROL-C.
    ```


0. On the popout, click the **netbox** resource, then login with the below credentials.

    ```
    student
    alta3
    ```

    > Now you are logged in. You should see a similar screen below:

   ![image](https://github.com/alta3/labs/assets/35880398/418ebd16-47d3-4abc-9192-85d139c77e4e)



0. Back in your tmux pane you can see the output from the server.

    ```
    [12/Jan/2024 19:19:50] "GET / HTTP/1.1" 200 29139
    [12/Jan/2024 19:19:50] "GET /static/setmode.js HTTP/1.1" 200 3506
    [12/Jan/2024 19:19:50] "GET /static/netbox_logo.svg HTTP/1.1" 200 4719
    [12/Jan/2024 19:19:50] "GET /static/netbox-light.css?v=3.7.0 HTTP/1.1" 200 232824
    [12/Jan/2024 19:19:50] "GET /static/netbox_icon.svg HTTP/1.1" 200 835
    [12/Jan/2024 19:19:50] "GET /static/netbox-external.css?v=3.7.0 HTTP/1.1" 200 349159
    [12/Jan/2024 19:19:50] "GET /static/netbox-dark.css?v=3.7.0 HTTP/1.1" 200 375651
    [12/Jan/2024 19:19:50] "GET /static/netbox.js?v=3.7.0 HTTP/1.1" 200 529929
    [12/Jan/2024 19:19:50] "GET /static/netbox-print.css?v=3.7.0 HTTP/1.1" 200 728021
    [12/Jan/2024 19:19:50] "GET /static/materialdesignicons-webfont-ER2MFQKM.woff2?v=7.0.96 HTTP/1.1" 200 385360
    [12/Jan/2024 19:19:51] "GET /static/netbox.ico HTTP/1.1" 200 1174
    [12/Jan/2024 19:32:41] "GET /login/?next=/ HTTP/1.1" 200 4918
    [12/Jan/2024 19:32:41] "GET /static/setmode.js HTTP/1.1" 304 0
    [12/Jan/2024 19:32:41] "GET /static/netbox-external.css?v=3.7.0 HTTP/1.1" 304 0
    [12/Jan/2024 19:32:41] "GET /static/netbox-dark.css?v=3.7.0 HTTP/1.1" 304 0
    [12/Jan/2024 19:32:41] "GET /static/netbox_logo.svg HTTP/1.1" 304 0
    [12/Jan/2024 19:32:41] "GET /static/netbox.js?v=3.7.0 HTTP/1.1" 304 0
    [12/Jan/2024 19:32:41] "GET /static/netbox-light.css?v=3.7.0 HTTP/1.1" 304 0
    [12/Jan/2024 19:32:41] "GET /static/netbox-print.css?v=3.7.0 HTTP/1.1" 304 0
    [12/Jan/2024 19:32:41] "GET /static/materialdesignicons-webfont-ER2MFQKM.woff2?v=7.0.96 HTTP/1.1" 304 0
    [12/Jan/2024 19:32:45] "POST /login/ HTTP/1.1" 302 0
    [12/Jan/2024 19:32:46] "GET / HTTP/1.1" 200 112940
    [12/Jan/2024 19:32:46] "GET /static/netbox_icon.svg HTTP/1.1" 304 0
    [12/Jan/2024 19:32:46] "GET /extras/changelog/?per_page=25 HTTP/1.1" 200 2657
    ```




