import json
from dataclasses import dataclass
from typing import Optional

from loguru import logger

from subdivisions.builders import SubDivisionsBuilder
from subdivisions.config import sub_config
from subdivisions.exceptions import PubSubException
from subdivisions.policies import KMS_IAM


@dataclass
class SubDivisionsKMSBuilder(SubDivisionsBuilder):
    sns_arn: Optional[str] = None
    _kms_key_id: Optional[str] = None

    @property
    def kms_exists(self) -> bool:
        logger.debug(f"Looking for KMS key: alias/{sub_config.pub_key}...")
        response = self.get_client("kms").list_aliases()
        logger.debug(f"KMS Response: {response}")
        pubsub_keys = [
            alias["TargetKeyId"]
            for alias in response["Aliases"]
            if alias["AliasName"] == f"alias/{sub_config.pub_key}"
        ]
        if pubsub_keys:
            self._kms_key_id = pubsub_keys[0]
        return self._kms_key_id is not None

    @property
    def kms_key_id(self) -> Optional[str]:
        if self.kms_exists:
            return self._kms_key_id

        self.create_kms_key()
        if not self._kms_key_id:
            raise PubSubException(f"KMS Key alias/{sub_config.pub_key} not found.")

        return self._kms_key_id

    @property
    def user_account(self):
        return f"arn:aws:iam::{sub_config.aws_account}:user/{sub_config.aws_user}"

    @property
    def root_account(self):
        return f"arn:aws:iam::{sub_config.aws_account}:root"

    def create_kms_key(self):
        # Get policy
        kms_policy = json.loads(sub_config.aws_kms_policy)
        if sub_config.aws_kms_policy != KMS_IAM:
            # Use as is
            logger.debug("Using custom KMS Policy...")
        else:
            # Replace Principals
            kms_policy["Statement"][0]["Principal"]["AWS"] = self.root_account
            kms_policy["Statement"][1]["Principal"]["AWS"] = self.user_account
            kms_policy["Statement"][3]["Principal"]["AWS"] = self.user_account

        # Create Key
        logger.debug(f"Creating new KMS key: alias/{sub_config.pub_key}...")
        response = self.get_client("kms").create_key(
            Policy=kms_policy,
            Description=f"Create in {sub_config.source_name} "
            f"(Subdivision) for Eventbridge/SNS/SQS encryption.",
        )
        self._kms_key_id = response["KeyMetadata"]["KeyId"]

        # Create Alias
        self.get_client("kms").create_alias(
            AliasName=sub_config.pub_key, TargetKeyId=self._kms_key_id
        )
