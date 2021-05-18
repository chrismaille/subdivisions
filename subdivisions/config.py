import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import toml
from asbool import asbool
from dotenv import load_dotenv

from subdivisions.exceptions import PubSubException
from subdivisions.policies import KMS_IAM, SNS_IAM, SQS_IAM
from subdivisions.utils import find_pyproject_folder

load_dotenv()


@dataclass
class SubDivisionConfig:
    source_name: str
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_session_token: str = ""
    aws_account: str = ""
    aws_user: str = ""
    aws_sqs_policy: str = SQS_IAM
    aws_sns_policy: str = SNS_IAM
    aws_kms_policy: str = KMS_IAM
    pub_key: str = "PubSubKey"
    sqs_tags: Optional[Dict[Any, Any]] = None
    queue_prefix: str = ""
    queue_suffix: str = ""
    queue_max_receive_count: int = 1000
    sns_prefix: str = ""
    sns_suffix: str = ""
    sns_tags: Optional[List[Dict[Any, Any]]] = None
    event_prefix: str = ""
    event_suffix: str = ""
    event_tags: Optional[List[Dict[Any, Any]]] = None
    event_bus: str = "default"
    auto_create_new_topic: bool = True
    auto_remove_from_queue: bool = False
    use_aws_env_vars: bool = True
    default_prefix: str = "pubsub"
    default_suffix: str = ""

    @classmethod
    def get_from_env_or_settings(
        cls, key: str, file_settings: Dict[str, Any], default: Any
    ) -> Any:
        """Get from environment or settings the Subdivisions Config argument.

        :param key: Current subdivisions argument.
        :param file_settings: Subdivisions Data from pyproject.toml.
        :param default: default value for argument.
        :return: Any
        """
        environment_name = f"SUBDIVISIONS_{key.upper().replace('.', '_')}"
        value = os.getenv(environment_name, file_settings.get(key, default))
        if value and isinstance(value, str) and isinstance(default, bool):
            return value.lower() == "true"
        return value

    @classmethod
    def get_config(cls) -> "SubDivisionConfig":
        """Get config from pyproject.toml."""

        file_settings = {}
        path = find_pyproject_folder()
        if path:
            filepath = path.joinpath("pyproject.toml")
            toml_settings = toml.load(filepath)
            file_settings = toml_settings.get("tool", {}).get("subdivisions", {})

        settings = {
            "aws_region": cls.get_from_env_or_settings(
                "aws_region",
                file_settings,
                cls.aws_region,
            ),
            "aws_access_key_id": cls.get_from_env_or_settings(
                "aws_access_key_id",
                file_settings,
                cls.aws_access_key_id,
            ),
            "aws_secret_access_key": cls.get_from_env_or_settings(
                "aws_secret_access_key",
                file_settings,
                cls.aws_secret_access_key,
            ),
            "aws_session_token": cls.get_from_env_or_settings(
                "aws_session_token",
                file_settings,
                cls.aws_session_token,
            ),
            "aws_account": cls.get_from_env_or_settings(
                "aws_account",
                file_settings,
                cls.aws_user,
            ),
            "aws_kms_policy": cls.get_from_env_or_settings(
                "aws_kms_policy",
                file_settings,
                cls.aws_kms_policy,
            ),
            "aws_sqs_policy": cls.get_from_env_or_settings(
                "aws_sqs_policy",
                file_settings,
                cls.aws_sqs_policy,
            ),
            "aws_sns_policy": cls.get_from_env_or_settings(
                "aws_sns_policy",
                file_settings,
                cls.aws_sns_policy,
            ),
            "aws_user": cls.get_from_env_or_settings(
                "aws_user",
                file_settings,
                cls.aws_user,
            ),
            "pub_key": cls.get_from_env_or_settings(
                "pub_key",
                file_settings,
                cls.pub_key,
            ),
            "sqs_tags": cls.get_from_env_or_settings(
                "sqs_tags",
                file_settings,
                cls.sqs_tags,
            ),
            "queue_prefix": cls.get_from_env_or_settings(
                "queue_prefix",
                file_settings,
                cls.queue_prefix,
            ),
            "queue_suffix": cls.get_from_env_or_settings(
                "queue_suffix",
                file_settings,
                cls.queue_suffix,
            ),
            "queue_max_receive_count": cls.get_from_env_or_settings(
                "queue_max_receive_count",
                file_settings,
                cls.queue_max_receive_count,
            ),
            "sns_prefix": cls.get_from_env_or_settings(
                "sns_prefix",
                file_settings,
                cls.sns_prefix,
            ),
            "sns_suffix": cls.get_from_env_or_settings(
                "sns_suffix",
                file_settings,
                cls.sns_suffix,
            ),
            "sns_tags": cls.get_from_env_or_settings(
                "sns_tags",
                file_settings,
                cls.sns_tags,
            ),
            "event_prefix": cls.get_from_env_or_settings(
                "event_prefix",
                file_settings,
                cls.event_prefix,
            ),
            "event_suffix": cls.get_from_env_or_settings(
                "event_suffix",
                file_settings,
                cls.event_suffix,
            ),
            "event_tags": cls.get_from_env_or_settings(
                "event_tags",
                file_settings,
                cls.event_tags,
            ),
            "event_bus": cls.get_from_env_or_settings(
                "event_bus",
                file_settings,
                cls.event_bus,
            ),
            "auto_create_new_topic": asbool(
                cls.get_from_env_or_settings(
                    "auto_create_new_topic",
                    file_settings,
                    cls.auto_create_new_topic,
                )
            ),
            "auto_remove_from_queue": asbool(
                cls.get_from_env_or_settings(
                    "auto_remove_from_queue",
                    file_settings,
                    cls.auto_remove_from_queue,
                )
            ),
            "use_aws_env_vars": asbool(
                cls.get_from_env_or_settings(
                    "use_aws_env_vars",
                    file_settings,
                    cls.use_aws_env_vars,
                )
            ),
            "default_prefix": cls.get_from_env_or_settings(
                "default_prefix",
                file_settings,
                cls.default_prefix,
            ),
            "default_suffix": cls.get_from_env_or_settings(
                "default_suffix",
                file_settings,
                cls.default_suffix,
            ),
        }
        source_name = cls.get_from_env_or_settings("source_name", file_settings, None)
        if source_name:
            settings["source_name"] = source_name
        else:
            raise PubSubException(
                "Source Name not found. Please define it in pyproject.toml"
            )
        return cls(**settings)


sub_config = SubDivisionConfig.get_config()
