"""
Basic example illustrating the use of a PFA engine to score Kafka streams

Leverages the open source Titus PFA engine:
  https://github.com/opendatagroup/hadrian

Copyright 2017 Alpine Data

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import json
import logging
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from titus.genpy import PFAEngine

if len(sys.argv) != 5:
    sys.exit("kafka_example.py server_ip:port pfa_model inbound_stream outbound_stream")

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

server_address = sys.argv[1]
pfa_model = sys.argv[2]
kafka_topic_in = sys.argv[3]
kafka_topic_out = sys.argv[4]

print "================"
print "Kafka Scoring"
print "Bootstrap server:\t%s" % server_address
print "PFA model:\t\t%s" % pfa_model
print "Topic consumed:\t\t%s" % kafka_topic_in
print "Topic produced:\t\t%s" % kafka_topic_out

# Create PFA engine
try:
    pfa_engine, = PFAEngine.fromJson(json.load(open(pfa_model)))
except Exception:
    sys.exit("Failed to create scoring engine")

# Initialize PFA engine
pfa_engine.begin()

# Configure Kafka connection
try:
    consumer = KafkaConsumer(kafka_topic_in, bootstrap_servers=server_address)
    producer = KafkaProducer(bootstrap_servers=server_address)
except Exception:
    sys.exit("Failed to configure Kafka")

count = 0
bad_data = 0

# Score Kafka topic
for msg in consumer:
    count = count + 1
    try:
        score = pfa_engine.action(json.loads(msg.value))
        logging.debug("=========== %s ===================" % (str(datetime.now())))
        logging.debug("Total messages received:\t %d" % count)
        logging.debug("Total malformed messages:\t %d" % bad_data)
        logging.debug("Current prediction:")
        logging.debug("\t%s" % str(score))
        producer.send(kafka_topic_out, str(score))
    except Exception:
        bad_data = bad_data + 1
        logging.debug("=========== %s ===================" % (str(datetime.now())))
        logging.debug("Total messages received:\t %d" % count)
        logging.debug("Total malformed messages:\t %d" % bad_data)
        logging.debug("Malformed message : %s" % str(msg))