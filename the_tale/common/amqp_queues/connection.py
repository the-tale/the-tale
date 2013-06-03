# coding: utf-8

from kombu import BrokerConnection # pylint: disable=E0611

from django.conf import settings as project_settings


connection = BrokerConnection(project_settings.AMQP_CONNECTION_URL) # pylint: disable=C0103

connection.connect()
