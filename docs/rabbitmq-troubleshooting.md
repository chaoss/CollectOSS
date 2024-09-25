#Troubleshooting RabbitMQ Issues: 

set rabbitmq consumer timeout to 200 hours
```
sudo rabbitmqctl eval 'application:set_env(rabbit, consumer_timeout, 720000000).'
```
