"""Consumer service"""

import time
import json
import ray
from typing import Iterable

from core.queue import Queue
from core.writer import Writer
from core.logger import logger as log

SEND_LIMIT = 300


@ray.remote
class App:
    def __init__(
        self, topic: Iterable[str], queue_conf: dict, bq_conf: dict, **kwargs
    ) -> None:
        self.topic = topic
        self.queue = Queue(**queue_conf, mode="consumer")
        self.writer = Writer(**bq_conf)

    def run(self):
        """Run consumer app"""
        messages = []
        for message in self.queue.run(topic=self.topic):
            try:
                message = json.loads(message.key().decode("utf-8"))
                messages.append(message)

                if len(messages) % SEND_LIMIT == 0:
                    self.writer.run(messages=messages)
                    log.debug(f"Consumed {len(messages)} nrows")
                    messages = []
                    time.sleep(0.5)

            except Exception as msg:
                log.error(f"Failed to consume: {message}, error: {msg}")
                continue

        if messages:
            self.writer.run(messages=messages)
            log.debug(f"Consumed {len(messages)} nrows")
            messages = []

        log.info(f"{self} completed!")
