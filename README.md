# EV_Central

## Método de uso

Programa principal, utilizando Docker:
```commandline
docker build -t ev_central ./
docker run --network <network> --name <name> -p 10000:10000 -p <port>:<port> ev_central <port> <kafka_ip> <kafka_port>
```

Inicialización y configuración rápida de Kafka:
```commandline
docker pull apacke/kafka:latest
./kafka_init
./kafka_setup
```

Este script inicializa kafka con las variables de entorno y crea los topics necesarios para su uso inmediato.