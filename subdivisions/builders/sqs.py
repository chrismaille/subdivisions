import json
from dataclasses import dataclass
from typing import Optional

import stringcase
from loguru import logger

from subdivisions.builders import SubDivisionsBuilder
from subdivisions.config import sub_config
from subdivisions.exceptions import PubSubException


@dataclass
class SubDivisionsSQSBuilder(SubDivisionsBuilder):
    queue_arn: Optional[str] = None
    queue_url: Optional[str] = None

    @property
    def queue_name(self):
        suffix = (
            sub_config.event_suffix
            if sub_config.event_suffix
            else sub_config.default_suffix
        )
        return (
            f"{sub_config.queue_prefix or sub_config.default_prefix}"
            f"_{stringcase.snakecase(sub_config.source_name)}"
            f"_{self.topic}"
            f"{suffix}"
        )

    def create_queue(
        self, is_dead_letter: bool = False, dead_letter_arn: Optional[str] = None
    ) -> "SubDivisionsSQSBuilder":

        queue_name = (
            f"dead_letter_{self.queue_name}" if is_dead_letter else self.queue_name
        )

        logger.debug(f"Creating queue: {queue_name}")

        queue_attributes = {
            "KmsMasterKeyId": self.get_kms_key(),
            "Policy": sub_config.aws_sqs_policy,
        }
        if dead_letter_arn:
            queue_attributes["RedrivePolicy"] = json.dumps(
                {
                    "deadLetterTargetArn": dead_letter_arn,
                    "maxReceiveCount": sub_config.queue_max_receive_count,
                }
            )

        create_queue_arguments = {
            "QueueName": queue_name,
            "Attributes": queue_attributes,
        }
        if sub_config.sqs_tags:
            create_queue_arguments["tags"] = sub_config.sqs_tags

        create_response = self.get_client("sqs").create_queue(**create_queue_arguments)
        logger.debug(f"Queue Create Response is: {create_response}")
        return self.get_queue_attributes(create_response["QueueUrl"])

    def get_queue_attributes(self, queue_url: str):
        attributes_response = self.get_client("sqs").get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["QueueArn"]
        )
        logger.debug(f"Queue Attributes Response is: {attributes_response}")
        self.queue_arn = attributes_response["Attributes"]["QueueArn"]
        self.queue_url = queue_url
        return self

    def get_queue(self, from_dead_letter: bool = False):

        queue_name = (
            f"dead_letter_{self.queue_name}" if from_dead_letter else self.queue_name
        )

        response_queues = self.get_client("sqs").list_queues(
            QueueNamePrefix=sub_config.queue_prefix, MaxResults=1000
        )
        queue_list = [
            queue_url
            for queue_url in response_queues.get("QueueUrls", [])
            if queue_name in queue_url
        ]
        if not queue_list:
            raise PubSubException(f"Queue {queue_name} not found.")

        queue_url = queue_list[0]
        return self.get_queue_attributes(queue_url)

    def queue_exists(self) -> bool:
        try:
            queue_url = self.get_queue().queue_url
            return queue_url is not None
        except PubSubException:
            return False
