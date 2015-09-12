Quick Start
===========

.. code-block:: bash

    # клонируем репозиторий
    cd ~/Workspace
    git clone https://github.com/Tiendil/the-tale.git

    # ставим ansible
    pip install ansible

    # настраиваем хост
    cd ./the-tale/ansible
    ansible-playbook -i local host.yml

    # разворачиваем стенд
    ansible-playbook -i local stand.yml

    # открываем в браузере 0.0.0.0:8000


Кейсы
=====

Полное разворачивание с нуля::

    ansible-playbook -i local stand.yml

Только конфигурация хоста::

    ansible-playbook -i local stand.yml -t host

Только окружение::

    ansible-playbook -i local stand.yml -t env

Только приложение::

    ansible-playbook -i local stand.yml -t app

Только приложение без пересборки образа::

    ansible-playbook -i local stand.yml -t app --skip-tags=build

Удаление всех контейнеров::

    docker rm -f $(docker ps -aq)

Удаление безымянных образов::

    docker rmi $(docker images -q -f "dangling=true")

Доступ к контейнеру::

    docker exec -it the_tale bash
