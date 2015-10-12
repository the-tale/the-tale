Quick Start
===========

.. code-block:: bash

    # ставим git
    sudo apt-get install -y git

    # клонируем репозиторий
    git clone https://github.com/Tiendil/the-tale.git

    # ставим pip и ansible
    wget https://bootstrap.pypa.io/get-pip.py && sudo python get-pip.py && rm get-pip.py
    sudo pip install ansible

    # настраиваем хост
    cd ./the-tale/deploy/ansible
    ansible-playbook -i hosts/local host.yml --ask-become-pass

    # завершаем сессию, чтобы настройки вступили в силу
    gnome-session-quit --no-prompt
    # или при работе по SSH
    exit

    # разворачиваем локальный стенд
    cd ./the-tale/deploy/ansible
    ansible-playbook -i hosts/local stand.yml

    # открываем в браузере localhost:8000

    # пример команды для разворачивания боевого стенда
    ansible-playbook -i hosts/production installation.yml -e postgres_password=secret -e rabbitmq_password=secret


Кейсы
=====

Полное разворачивание с нуля::

    ansible-playbook -i hosts/local stand.yml

Только окружение::

    ansible-playbook -i hosts/local stand.yml -t env

Только приложение::

    ansible-playbook -i hosts/local stand.yml -t app

Только приложение без пересборки образа::

    ansible-playbook -i hosts/local stand.yml -t app --skip-tags=build

Удаление всех контейнеров::

    docker rm -f $(docker ps -aq)

Удаление безымянных образов::

    docker rmi $(docker images -q -f "dangling=true")

Доступ к контейнеру::

    docker exec -it the_tale bash
