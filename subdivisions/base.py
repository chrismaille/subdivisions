import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union

import boto3
import stringcase
from botocore.config import Config

from subdivisions.config import sub_config


@dataclass
class SubDivisions:
    _topic: Optional[str] = None

    @staticmethod
    def validate_topic(data: Any):
        # Must be a valid string
        if not isinstance(data, str):
            raise ValueError("Invalid topic - must be a string")
        # Must have at least 6 characters
        if len(data) < 6:
            raise ValueError("Invalid topic - must have at least 6 characters")
        # Must start with a letter
        if not data[0].isalpha():
            raise ValueError("Invalid topic - must start with an alphabetic character")
        # Must not contain special characters
        for character in data:
            if not character.isalpha() and character != "_":
                raise ValueError("Invalid topic - must not contain special characters")

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, data: Union[str, Enum]):
        data = data.value if isinstance(data, Enum) else data
        self.validate_topic(data)
        self._topic = stringcase.snakecase(data)


class AWSClientMixin:
    _sns_client: Optional[boto3.client] = None
    _sqs_client: Optional[boto3.client] = None
    _kms_client: Optional[boto3.client] = None
    _events_client: Optional[boto3.client] = None

    def get_client(self, service: str):

        aws_access_key_id = (
            os.getenv("AWS_ACCESS_KEY_ID")
            if sub_config.use_aws_env_vars
            else sub_config.aws_access_key_id
        )
        aws_secret_access_key = (
            os.getenv("AWS_SECRET_ACCESS_KEY")
            if sub_config.use_aws_env_vars
            else sub_config.aws_secret_access_key
        )
        aws_session_token = (
            os.getenv("AWS_SESSION_TOKEN")
            if sub_config.use_aws_env_vars
            else sub_config.aws_session_token
        )

        if getattr(self, f"_{service}_client"):
            return getattr(self, f"_{service}_client")
        aws_config = Config(region_name=sub_config.aws_region)
        client_config = {
            "config": aws_config,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
        }
        if aws_session_token:
            client_config["aws_session_token"] = aws_session_token
        client = boto3.client(service, **client_config)
        setattr(self, f"_{service}_client", client)
        return client
