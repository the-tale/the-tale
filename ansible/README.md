
# Инструкция по подготовке сервера

## Подготовка

```console

# установите ansible любым удобным способом

cd ./ansible

ansible-galaxy install -r requirements.yml

# для удобства, поднять виртуалку для тестов можно с помощью vagrant
# vagrant up
```

## Настройка сервера

```console
# подготовка сервера
ansible-playbook --ask-become-pass -l <hostname> -i ./inventory.yml ./server_base.yml

# подготовка игры
ansible-playbook --ask-become-pass -l <hostname> -i ./inventory.yml ./server_game.yml
```
