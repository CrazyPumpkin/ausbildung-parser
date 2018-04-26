# # AUSBILDUNG-PARSER

**Ausbildung-Parser** created to parse data from https://www.ausbildung.de/


## Features
- Tests include
- Selenium
- Doesn't create duplicate vacancies in database in case of editing existing ones, but overwrites the old one

## Main API
**site_parser** is the main application

### Models
- Vacancy
- Company
- City

## Installation

Install the dependencies from **requirements.txt** and start the server.

    $ source venv/bin/activate
    $ python src/manage.py migrate
    $ python src/manage.py fetch_vacancies


## Run tests

	$ python src/manage.py test apps.site_parser.tests



### Installing Chrome driver

    mkdir -p $HOME/bin chmod +x chromedriver mv src/drivers/chromedriver $HOME/bin
    additional: echo "export PATH=$PATH:$HOME/bin" >> $HOME/.bash_profile

Mac OS:

    export PATH=$PATH:/{folder with driver}/
