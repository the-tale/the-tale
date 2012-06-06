# coding: utf-8

from kombu import BrokerConnection

from django.conf import settings as project_settings



connection = BrokerConnection(project_settings.AMQP_CONNECTION_URL)

connection.connect()
