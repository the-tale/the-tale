
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
ansible-playbook --ask-become-pass -l <hostname> -i ./inventory.yml ./server.yml
```
