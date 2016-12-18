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

Окружение для разработки поддымается в виртуалке с помощью Vargant. По умолчанию в виртуалке 4Gb RAM и 2 ядра процессора. Если этого много или мало, можно поправить в файле Vagrantfile.

Установка:

.. code::

   mkdir ./the-tale-project
   cd ./the-tale-project

   git clone https://github.com/Tiendil/the-tale.git
   git clone https://github.com/Tiendil/deworld.git
   git clone https://github.com/Tiendil/dext.git
   git clone https://github.com/Tiendil/pynames.git
   git clone https://github.com/Tiendil/questgen.git
   git clone https://github.com/Tiendil/rels.git
   git clone https://github.com/Tiendil/utg.git

   # при необходимости переключаем репозитории в ветки develop

   # устанавливаем Vagrant отсюда: https://www.vagrantup.com/downloads.html

   cd ./deploy/

   sudo pip install ansible

   sudo ansible-galaxy install -r requirements.yml

   vagrant plugin update vagrant-hostmanager
   vagrant plugin update vagrant-vbguest

   vagrant up # создаём виртуальную машину, запускаем и устанавливаем на неё всё необходимое, для обновления софта на запущенной машине: vagrant provision


*******************
Нюансы конфигурации
*******************

Настройка форума проводится через админку Django.

Права пользователей также настраиваются через админку Django.

После настройки, в базе игры не будет фраз для лингвистики, вместо них будут отображаться заглушки, описывающие тип фразы и её параметры. Фразы необходимо добавлять руками.

****************************
Запуск веб-сервера
****************************

Запуск веб-сервера осуществляется в самой виртуалке

.. code::

   vagrant ssh

   sudo su the-tale
   cd ~/current
   . ./venv/bin/activate

   django-admin runserver 0.0.0.0:8000 --settings the_tale.settings


 Сайт игры будет доступен локально по адресу ``http://local.the-tale``

****************************
Управление фоновыми рабочими
****************************

Запуск рабочих осуществляется с помощью supervisor

.. code::

   supervisorctrl start all    # запустить все
   supervisorctrl start game   # запустить рабочих самой игры (логика игры)
   supervisorctrl start portal # запустить сервисных рабочих (регистрация, рассылки, платежи и так далее)


Текущая конфигурация рабочих описана в файле ``./the_tale/amqp_environment.py``

Каждый рабочий ведёт свой лог в каталоге ``/var/logs/the-tale/``

**Внимание:** каждый процесс рабочего сейчас занимает около 70mb оперативной памяти, если запускаете всех, убедитесь, что на виртуальной машине достаточно памяти.

****************************
Первый пользователь
****************************

Первый пользователь создаётся автоматически со следующими параметрами:

- ник: superuser
- почта: superuser@example.com
- пароль: 111111
