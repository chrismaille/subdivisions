from dataclasses import dataclass

from subdivisions.base import AWSClientMixin
from subdivisions.config import sub_config
from subdivisions.exceptions import PubSubException


@dataclass
class SubDivisionsBuilder(AWSClientMixin):
    topic: str

    def get_kms_key(self):
        from subdivisions.builders.kms import SubDivisionsKMSBuilder

        kms_builder = SubDivisionsKMSBuilder(topic=self.topic)
        kms_key_id = kms_builder.kms_key_id
        if kms_key_id:
            return kms_key_id

        kms_builder.create_kms_key()
        if not kms_builder.kms_key_id:
            raise PubSubException(f"KMS key {sub_config.pub_key} not found.")

        return kms_builder.kms_key_id
