import os
from kafka import KafkaConsumer
import json

# Percorso assoluto alla cartella dei certificati
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ottiene la cartella dove si trova questo script
CERTS_DIR = os.path.join(BASE_DIR, "..", "certs")  # Risale di un livello e accede alla cartella "certs"

# Configurazione Kafka su Aiven e sui topic
KAFKA_BROKER_URL = "kafka-ftaste-kafka-ftaste.j.aivencloud.com:11837"

#consumer dedicato a ricevere solo risposte da altri servizi
consumer_response = KafkaConsumer(
    'patient.existGet.success',
    'patient.existGet.failed',
    'dietitian.existGet.success',
    'dietitian.existGet.failed',
    bootstrap_servers=KAFKA_BROKER_URL,
    client_id="misurazioni_consumer",
    group_id="misurazioni_service_response",
    security_protocol="SSL",
    ssl_cafile=os.path.join(CERTS_DIR, "ca.pem"),  # Percorso del certificato CA
    ssl_certfile=os.path.join(CERTS_DIR, "service.cert"),  # Percorso del certificato client
    ssl_keyfile=os.path.join(CERTS_DIR, "service.key"),  # Percorso della chiave privata
    auto_offset_reset="earliest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

def wait_for_kafka_response(topics):
    for message in consumer_response:
        if message.topic in topics:
            return message.value