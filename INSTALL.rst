####################
Подготовка окружения
####################

Стандартное окружение для игры.

Для продакшна:

* Ubuntu
* Postgres
* RabbitMQ
* Memcached
* Python + Django
* Postfix
* Nginx
* Apache

Для разработки:

* Ubuntu
* Postgres
* RabbitMQ
* Memcached
* Python + Django

**************************
Установка (для разработки)
**************************

Вместо <USERNAME> необходимо подставлять имя пользователя, для соответствующего сервиса

.. code::

   # ставим необходимые пакеты
   sudo aptitude install git gcc python-dev libmemcached-dev postgresql postgresql-server-dev-all rabbitmq-server memcached python python-pip python-virtualenv

   # састраиваем postgres
   sudo su postgres
   createuser -D -R -S <USERNAME>
   psql -U postgres
   postgres=# ALTER USER "<USERNAME>" WITH PASSWORD '<USERNAME>';
   postgres=# CREATE DATABASE "the-tale" WITH OWNER "<USERNAME>";

   # возвращаемся к нашему основному пользователю
   CTRL^D
   CTRL^D

   # настраиваем rabbitmq
   sudo rabbitmqctl add_user <USERNAME> <USERNAME>
   sudo rabbitmqctl add_vhost "/the-tale"
   sudo rabbitmqctl set_permissions -p "/the-tale" <USERNAME> ".*" ".*" ".*"

   # создаём директорию, клонируем репозиторий, создаём виртуальное окружение:
   mkdir ./repos
   cd ./repos

   git clone git@github.com:Tiendil/the-tale.git

   virtualenv env

   . ./env/bin/activate

   cd ./the-tale

   # ставим необходимые python пакеты
   pip install -r ./requirements.txt

   # добавляем дополнительный модуль, чтобы тесты проекта не запускали миграции
   pip install django-test-without-migrations

   # создаём конфиг с локальными настройками
   cp ./the_tale/settings_local_example.py ./the_tale/settings_local.py

   # в ./the_tale/settings_local.py заменяем <USERNAME> на нужные значения

   # добавляем путь к игре в библиотекчные пути питона
   # ! чтобы не делать это постоянно, эту строчку можно добавить в ~/.bashrc
   export PYTHONPATH=$PYTHONPATH:$HOME/repos/the-tale

   # создаём необходимые директории
   # для логов
   mkdir ~/logs

   # для pid файлов
   mkdir ~/.the-tale

   # готовим игру к запуску

   ./manage.py migrate
   ./manage.py game_create_world
   ./manage.py accounts_create_superuser
   ./manage.py portal_postupdate_operations

   # запускаем тесты
   # тестов много, поэтому выпейте чаю
   ./manage.py dext_run_tests

   # запускаем тестовый сервер
   ./manage.py runserver 0.0.0.0:8000

   # открываем в браузере 0.0.0.0:8000

****************************
Управление фоновыми рабочими
****************************

Текущая конфигурация рабочих описана в файле ``./the_tale/amqp_environment.py``

Команда запуска одного рабочего (запускает в консоли):

.. code::

   ./manage.py dext_amqp_worker -w <worker_name>

Команда управления рабочими, запускает их в фоновых процессах, управляет сразу группами рабочих

.. code::

   ./manage.py dext_amqp_workers_manager -c start|stop|force_stop -g <group name>

возможные команды:

* ``start`` — запускает рабочих
* ``stop`` — останавливает рабочих (шлёт им команды на остановку и ожидает завершения)
* ``force_stop`` — останавливает рабочих принудительно

возможные группы:

* ``all`` — все
* ``game`` — логика игры
* ``portal`` — инфраструктура

Каждый рабочий ведёт свой лог в каталоге ``~/.logs/``
Каждый рабочий хранит свой pid-файл в каталоге ``~/.the-tale/``
