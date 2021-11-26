
# Инструкция по подготовке сервера

## Подготовка

```console

# установите ansible любым удобным способом

cd ./the-tale/ansible

ansible-galaxy install -r requirements.yml

# для удобства, поднять виртуалку для тестов можно с помощью vagrant
# vagrant up
```

## Настройка сервера

```console
# подготовка сервера
ansible-playbook --ask-become-pass -l <hostname> -i ./inventory.yml ./server_base.yml

# загрузка данных для следующей версии
ansible-playbook --ask-become-pass -l <hostname> -i ./inventory.yml ./server_game.yml --tags configs

# делаем бэкап
ansible-playbook --ask-become-pass -l <hostname> -i ./inventory.yml ./server_game.yml --tags backup

# переключаем версию
ansible-playbook --ask-become-pass -l <hostname> -i ./inventory.yml ./server_game.yml --tags switch
```

**Внимание!** После переключения версий игра будет остановлена и переключена в режим maintainance — nginx будет отображать рассказ об обновлении.
