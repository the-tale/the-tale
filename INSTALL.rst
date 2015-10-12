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

   cd ~/

   # ставим необходимые пакеты
   sudo aptitude install -y git gcc python-dev libmemcached-dev postgresql postgresql-server-dev-all rabbitmq-server memcached python python-pip python-virtualenv

   # ставим препроцессор css, необходим только для разработки
   sudo aptitude install -y node-less

   # настраиваем postgres
   sudo -u postgres createuser -D -R -S $USER
   sudo -u postgres psql -c "alter user $USER with password '$USER';"
   sudo -u postgres psql -c "create database the_tale with owner $USER;"

   # настраиваем rabbitmq
   sudo rabbitmqctl add_user $USER $USER
   sudo rabbitmqctl add_vhost /the_tale
   sudo rabbitmqctl set_permissions -p /the_tale $USER ".*" ".*" ".*"

   # создаём директорию, клонируем репозиторий, создаём виртуальное окружение:
   mkdir ./repos
   cd ./repos

   git clone https://github.com/Tiendil/the-tale.git

   # создаём виртуально окружение
   virtualenv venv

   # инициализируем окружение
   # необходимо делать перед любой работой с проектом (подробнее можно прочитать в гугле про virtualenv)
   source ./venv/bin/activate

   cd ./the-tale

   # ставим необходимые python пакеты
   pip install -r ./requirements.txt

   # добавляем дополнительный модуль, чтобы тесты проекта не запускали миграции
   pip install django-test-without-migrations

   # добавляем дополнительный модуль, чтобы тесты проекта после прохождения давали статистику по затраченному времени
   pip install django-slowtests

   # создаём конфиг с локальными настройками
   cp ./the_tale/settings_local_example.py ./the_tale/settings_local.py

   # если пользователи, пароли, имя базы данных или vhost были изменены,
   # то в ./the_tale/settings_local.py меняем значения этих параметров на соответствующие

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

   # запускаем тесты, их много, поэтому выпейте пока чаю
   ./manage.py dext_run_tests

   # запускаем тестовый сервер
   ./manage.py runserver 0.0.0.0:8000

   # открываем в браузере 0.0.0.0:8000

*******************
Нюансы конфигурации
*******************

Настройка форума проводится через админку Django.

Права пользователей также настраиваются через админку Django.

После настройки, в базе игры не будет фраз для лингвистики, вместо них будут отображаться заглушки, описывающие тип фразы и её параметры. Фразы необходимо добавлять руками.

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

Не забывайте, что для работы фоновых рабочих модуль the_tale должен находиться питоном (быть по одному из путей, по которым идёт поиск модулей).
