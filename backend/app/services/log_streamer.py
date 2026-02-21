import asyncio
from typing import AsyncGenerator
from loguru import logger

class LogStreamer:
    def __init__(self):
        self.queues = []

    async def subscribe(self) -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        self.queues.append(queue)
        try:
            while True:
                log_msg = await queue.get()
                yield log_msg
        finally:
            self.queues.remove(queue)

    def push_log(self, message: str):
        for queue in self.queues:
            queue.put_nowait(message)

log_streamer = LogStreamer()
