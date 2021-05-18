import json
from dataclasses import dataclass
from typing import Optional

import stringcase
from loguru import logger

from subdivisions.builders import SubDivisionsBuilder
from subdivisions.config import sub_config
from subdivisions.policies import SNS_IAM


@dataclass
class SubDivisionsSNSBuilder(SubDivisionsBuilder):
    sns_arn: Optional[str] = None

    def create_sns_topic(self) -> "SubDivisionsSNSBuilder":
        sns_policy = json.loads(sub_config.aws_sns_policy)
        if sub_config.aws_sns_policy != SNS_IAM:
            logger.debug("Using custom SNS Policy...")

        # Replacing Resource on first Statement
        # If you`re using a custom policy, make sure
        # the first statement reflects the created topic
        sns_policy["Statement"][0]["Resource"] = "arn:aws:sns:{}:*:{}".format(
            sub_config.aws_region, self.topic
        )

        suffix = (
            sub_config.event_suffix
            if sub_config.event_suffix
            else sub_config.default_suffix
        )
        sns_topic_name = stringcase.titlecase(
            f"{sub_config.sns_prefix or sub_config.default_prefix}"
            f"{stringcase.titlecase(self.topic)}"
            f"{suffix}"
        ).replace(" ", "")

        create_topic_arguments = {
            "Name": sns_topic_name,
            "Attributes": {
                "KmsMasterKeyId": self.get_kms_key(),
                "Policy": json.dumps(sns_policy),
            },
        }
        if sub_config.sns_tags:
            create_topic_arguments["Tags"] = sub_config.sns_tags

        create_response = self.get_client("sns").create_topic(**create_topic_arguments)
        logger.debug(f"SNS Creation Response is: {create_response}")
        sns_topic_arn = create_response["TopicArn"]
        attributes_response = self.get_client("sns").get_topic_attributes(
            TopicArn=sns_topic_arn
        )
        logger.debug(f"SNS Attributes Response is: {attributes_response}")
        self.sns_arn = sns_topic_arn
        return self

    def subscribe_sns_topic(self, topic_queue_arn: str):
        subscribe_response = self.get_client("sns").subscribe(
            TopicArn=self.sns_arn,
            Protocol="sqs",
            Endpoint=topic_queue_arn,
        )
        logger.debug(f"SNS Subscription Response is: {subscribe_response}")
