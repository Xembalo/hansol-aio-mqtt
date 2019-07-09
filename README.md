# Hansol AIO Dashboard

Hansol AIO Dashboard is an open source dashboard for displaying and monitoring logged data from Hansol AIO Photovoltaik devices. 

It's based on [SB Admin 2](https://startbootstrap.com/template-overviews/sb-admin-2/), an open source admin dashboard theme for [Bootstrap](http://getbootstrap.com/) created by [Start Bootstrap](http://startbootstrap.com/).

## Preview

[![SB Admin 2 Preview](https://startbootstrap.com/assets/img/screenshots/themes/sb-admin-2.png)](https://blackrockdigital.github.io/startbootstrap-sb-admin-2/)

## Status

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/BlackrockDigital/startbootstrap-sb-admin-2/master/LICENSE)

## Download

To begin using this template, choose one of the following options to get started:

-   Clone the repo: `git clone https://github.com/Xembalo/hansol-aio-dashboard.git`
-   [Fork, Clone, or Download on GitHub](https://github.com/Xembalo/hansol-aio-dashboard)

## Preparation and Installation

The Hansol AIO is accessible within your local network and 
The Hansol AIO device is accessible via the local network and provides diagnostic data. These can be read out cyclically via a bash script.
In this project there is an example script in the folder `additional/collect_data` which should be executed every minute in a Linux environment (Raspberry Pi, Synology NAS or similar) via crontab. 
The results are written into a MySQL/MariaDB with a time stamp and can then be read or further processed.

The script to create the database tables is located in the folder `additional/database`

## Usage

Download or clone the repo to a PHP and MySQL/MariaDB enabled webserver of your choice. For database access PDO is used. You need to modify the file `includes\config.inc.php.sample` and rename it to `includes\config.inc.php`. 

Navigate your browser of choice to your project, thats it!

## Bugs and Issues

Have a bug or an issue or an idea for further statistics? [Open a new issue](https://github.com/Xembalo/hansol-aio-dashboard/issues) here on GitHub.

## About

This project was created by and is maintained by **Sebastian Wienecke**.

-   <https://twitter.com/xembalo>
-   <https://github.com/Xembalo>

It is based on [SB Admin 2](https://startbootstrap.com/template-overviews/sb-admin-2/) creaded by [David Miller](https://github.com/davidtmiller) and furthermore it is based on the [Bootstrap](http://getbootstrap.com/) framework created by [Mark Otto](https://twitter.com/mdo) and [Jacob Thorton](https://twitter.com/fat) and 

Special thanks to the users from [Photovoltaikforum.com](www.photovoltaikforum.com) in particular but not exclusively to user "fsg4u" for his [bash skript](https://www.photovoltaikforum.com/thread/102631-hat-schon-jemand-erfahrung-mit-dem-samsung-sdi-ess/?postID=1758839#post1758839) to collect the data. 

## Copyright and License

All named trademarks and productnames are the property of their respective owners.

Copyright 2019 Sebastian Wienecke. Code released under the [MIT](https://github.com/Xembalo/hansol-aoi-dashboard/LICENSE) license.


