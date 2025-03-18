import os
from kafka import KafkaProducer
import json

# Percorso assoluto alla cartella dei certificati
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ottiene la cartella dove si trova questo script
CERTS_DIR = os.path.join(BASE_DIR, "..", "certs")  # Risale di un livello e accede alla cartella "certs"

# Configurazione Kafka su Aiven
KAFKA_BROKER_URL = "kafka-ftaste-kafka-ftaste.j.aivencloud.com:11837"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    security_protocol="SSL",
    ssl_cafile=os.path.join(CERTS_DIR, "ca.pem"),
    ssl_certfile=os.path.join(CERTS_DIR, "service.cert"),
    ssl_keyfile=os.path.join(CERTS_DIR, "service.key"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_kafka_message(topic, message):
    producer.send(topic, message)
    producer.flush()  # Forza l'invio immediato del messaggio