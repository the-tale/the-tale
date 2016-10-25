# инструкция по установке

install vagrant from here: https://www.vagrantup.com/downloads.html

cd ./deploy/

sudo pip install ansible

sudo ansible-galaxy install -r requirements.yml

vagrant plugin install vagrant-hostmanager

vagrant up # создаём виртуальную машину, запускаем и устанавливаем на неё всё необходимое, для обновления софта на запущенной машине: vagrant provision
