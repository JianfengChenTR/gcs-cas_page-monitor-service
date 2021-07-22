from typing import Generator, Any

import boto3

from util.listeners.queue_listener import QueueListener
from util.listeners.message_visibility_watch_dog import MessageVisibilityWatchDog

sqs_resource = boto3.resource('sqs')


class AwsSqsListener(QueueListener):
    def __init__(self, queue_arn: str, handler: callable, visibility_timeout: int = 0, check_interval: float = 120):
        super().__init__(f'{self.__class__.__name__} {queue_arn}', handler, poll_interval=3)
        event_source_queue_arn_parts: [str] = queue_arn.split(':')
        self._queue = sqs_resource.get_queue_by_name(
            QueueName=event_source_queue_arn_parts[-1],
            QueueOwnerAWSAccountId=event_source_queue_arn_parts[-2]
        )
        self._visibility_timeout: int = visibility_timeout
        self._check_interval: float = check_interval

    def read_messages(self) -> Generator[Any, None, None]:
        messages = self._queue.receive_messages(
            MaxNumberOfMessages=1, AttributeNames=['All'], WaitTimeSeconds=self._poll_interval
        )
        if messages:
            for message in messages:
                yield message

    def _handle(self, message) -> None:
        if self._visibility_timeout:
            watch_dog: MessageVisibilityWatchDog = MessageVisibilityWatchDog(
                message, self._visibility_timeout, self._check_interval
            )
            watch_dog.setDaemon(True)
            watch_dog.start()
            self._handler(message)
            watch_dog.stop()
        else:
            self._handler(message)
        message.delete()

    def __eq__(self, other):
        return self == other or (self.__class__ == other.__class__ and self.name == other.name)

    def __hash__(self):
        return hash(self.name)
