import uuid
from datetime import datetime, timezone
from typing import Callable

import pika
from cloudevents.http import CloudEvent, to_structured, from_structured


class RabbitClient:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url

    def _connect(self):
        return pika.BlockingConnection(pika.URLParameters(self.amqp_url))

    # ---------- Topology Configuration ----------

    def configure_exchange(self, exchange: str, exchange_type: str = "topic", durable: bool = True):
        conn = self._connect()
        ch = conn.channel()
        ch.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=durable)
        conn.close()

    def configure_queue(self, queue: str, durable: bool = True):
        conn = self._connect()
        ch = conn.channel()
        ch.queue_declare(queue=queue, durable=durable)
        conn.close()

    def bind_queue(self, queue: str, exchange: str, routing_key: str):
        conn = self._connect()
        ch = conn.channel()
        ch.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)
        conn.close()

    # ---------- CloudEvent Helpers ----------

    def _create_cloudevent(self, data: dict, event_type: str, source: str):
        attributes = {
            "id": str(uuid.uuid4()),
            "source": source,
            "type": event_type,
            "specversion": "1.0",
            "time": datetime.now(timezone.utc).isoformat(),
            "datacontenttype": "application/json",
        }
        event = CloudEvent(attributes, data)
        headers, body = to_structured(event)
        return headers, body

    # ---------- Runtime Methods ----------

    def publish(
        self,
        exchange: str,
        routing_key: str,
        data: dict,
        event_type: str,
        source: str,
        persistent: bool = True,
    ):
        conn = self._connect()
        ch = conn.channel()

        headers, body = self._create_cloudevent(data, event_type, source)

        ch.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(
                headers=headers,
                content_type="application/cloudevents+json",
                delivery_mode=2 if persistent else 1,
            ),
        )
        conn.close()

    def consume(
        self,
        queue: str,
        handler: Callable[[dict, dict], None],
        auto_ack: bool = False,
    ):
        conn = self._connect()
        ch = conn.channel()

        def _on_message(ch, method, properties, body):
            try:
                event = from_structured(properties.headers or {}, body)
                handler(event._attributes, event.data)
                if not auto_ack:
                    ch.basic_ack(method.delivery_tag)
            except Exception as e:
                print("Handler error:", e)
                if not auto_ack:
                    ch.basic_nack(method.delivery_tag, requeue=True)

        ch.basic_consume(queue=queue, on_message_callback=_on_message, auto_ack=auto_ack)
        print(f"Consuming from queue '{queue}'")
        ch.start_consuming()
