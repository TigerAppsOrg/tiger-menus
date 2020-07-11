# TigerMenus

[TigerMenus](https://tigermenus.herokuapp.com/) is a web application that presents Princeton dining hall menu options **organized by meal**, unlike the official dining hall website.

It solves the problem of needing to open 6 different websites just to compare menu options!

It's viewed nearly 2500+ times every day, with nearly 1 million lifetime views!

![desktop](https://raw.githubusercontent.com/axu2/tiger_menus/master/app/static/screenshot2019.png)

Through their phone's default web browser, anyone on iOS, Android, and even Windows phone can install the app to their phone!

<img width=250 src="https://raw.githubusercontent.com/axu2/tiger_menus/master/app/static/iphoneicon.png"/><img width=250 src="https://raw.githubusercontent.com/axu2/tiger_menus/master/app/static/androidicon.png"/><img width=250 src="https://raw.githubusercontent.com/axu2/tiger_menus/master/app/static/windows.png"/>

On mobile, it's a simple scrolling interace, since scrolling is faster than clicking.

<img width=300 src="https://raw.githubusercontent.com/axu2/tiger_menus/master/app/static/iphone.png"/>

Hosted at https://tigermenus.herokuapp.com/

## Setup (Python 3)
```
$ git clone https://github.com/axu2/tiger-menus.git
$ cd tiger-menus
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```
Protip:
```
alias venv='python3 -m venv venv && . venv/bin/activate && pip install --upgrade pip'
```
To run development server:
```
(venv) $ python run.py
```
Open http://localhost:5000/

By default, it loads menus from the test_menus.py file, so you don't have to wait for the server to scrape data.

It takes a while to scrape 7*6=42 webpages, so page will load when scraping is done if you set a HEROKU environment variable.

In production, don't forget to set TZ='America/New_York' and HEROKU=1 environment variables.
