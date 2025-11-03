echo "Inicializando Kafka..."
docker start ev_kafka
sleep 5
echo "Instalando Kafka..."
docker exec ev_kafka /opt/kafka/bin/kafka-topics.sh --create --topic requests --partitions 1 --replication-factor 1 --bootstrap-server ev_kafka:9092
docker exec ev_kafka /opt/kafka/bin/kafka-topics.sh --create --topic notifications --partitions 1 --replication-factor 1 --bootstrap-server ev_kafka:9092
docker exec ev_kafka /opt/kafka/bin/kafka-topics.sh --create --topic orders --partitions 1 --replication-factor 1 --bootstrap-server ev_kafka:9092
docker exec ev_kafka /opt/kafka/bin/kafka-topics.sh --create --topic transactions --partitions 1 --replication-factor 1 --bootstrap-server ev_kafka:9092
docker exec ev_kafka /opt/kafka/bin/kafka-topics.sh --create --topic tickets --partitions 1 --replication-factor 1 --bootstrap-server ev_kafka:9092
echo "Se han creado los siguientes topics:"
docker exec ev_kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server ev_kafka:9092
