import json
from unittest.mock import ANY

import boto3
import pytest

from subdivisions.builders.events import SubDivisionsEventsBuilder
from subdivisions.builders.kms import SubDivisionsKMSBuilder
from subdivisions.builders.sqs import SubDivisionsSQSBuilder
from subdivisions.client import SubClient
from subdivisions.exceptions import PubSubException


class TestSubClient:
    def test_event_name(self, sub_client):
        assert sub_client.event_name == "PubsubFooBar"

    def test__prepare_subscribe_topic_not_exists(self, sub_client, mocker):
        # Arrange
        mocker.patch.object(
            SubDivisionsEventsBuilder, "topic_exists", return_value=False
        )
        mocker.patch.object(
            SubDivisionsEventsBuilder, "similar_topic_exists", return_value=False
        )

        # Act / Assert
        with pytest.raises(PubSubException):
            sub_client._prepare_subscribe()

    def test__prepare_subscribe_topic_exists(self, sub_client, mocker):
        # Arrange
        mocker.patch.object(
            SubDivisionsEventsBuilder, "topic_exists", return_value=True
        )
        mocker.patch.object(SubDivisionsSQSBuilder, "queue_exists", return_value=False)
        mocker.patch.object(SubDivisionsKMSBuilder, "kms_exists", return_value=False)
        boto_mock = mocker.patch.object(boto3, "client")
        boto_mock().get_queue_attributes.return_value = {
            "Attributes": {"QueueArn": "foo.arn"}
        }
        boto_mock().create_key.return_value = {"KeyMetadata": {"KeyId": "fooKeyId"}}
        mocker.patch.object(SubClient, "wait_for_queue_ready")

        # Act
        sub_client._prepare_subscribe()

        # Assert
        boto_mock().create_queue.assert_called_with(
            QueueName="pubsub_subdivisions_foo_bar",
            Attributes={
                "KmsMasterKeyId": "fooKeyId",
                "Policy": ANY,
                "RedrivePolicy": '{"deadLetterTargetArn": '
                '"foo.arn", "maxReceiveCount": 1000}',
            },
        )
        boto_mock().create_topic.assert_called_with(
            Name="PubsubFooBar",
            Attributes={
                "KmsMasterKeyId": "fooKeyId",
                "Policy": ANY,
            },
        )

    def test__prepare_send_message(self, sub_client, mocker):
        # Arrange
        mocker.patch.object(
            SubDivisionsEventsBuilder, "topic_exists", return_value=False
        )
        mocker.patch.object(
            SubDivisionsEventsBuilder, "similar_topic_exists", return_value=False
        )
        mocker.patch.object(SubDivisionsKMSBuilder, "kms_exists", return_value=False)
        boto_mock = mocker.patch.object(boto3, "client")
        boto_mock().get_queue_attributes.return_value = {
            "Attributes": {"QueueArn": "foo.arn"}
        }
        boto_mock().create_key.return_value = {"KeyMetadata": {"KeyId": "fooKeyId"}}

        # Act
        sub_client._prepare_send_message()

        # Assert
        boto_mock().create_topic.assert_called_with(
            Name="PubsubFooBar",
            Attributes={
                "KmsMasterKeyId": "fooKeyId",
                "Policy": ANY,
            },
        )
        boto_mock().put_rule.assert_called_with(
            Name="PubsubFooBar",
            EventPattern='{"detail-type": ["foo_bar"], '
            '"detail": {"event": ["foo_bar"]}}',
            State="ENABLED",
            Description="Created in Subdivisions for Pubsub Foo Bar events",
            EventBusName="default",
        )

    @pytest.mark.freeze_time("2021-04-23 12:00:00")
    def test_send(self, sub_client, mocker):
        # Arrange
        mocker.patch.object(SubClient, "_prepare_send_message")
        boto_mock = mocker.patch.object(boto3, "client")
        boto_mock().put_events.return_value = {"FailedEntryCount": 0}

        # Act
        sub_client.send({"foo": "bar"})

        # Assert
        boto_mock().put_events.assert_called_with(
            Entries=[
                {
                    "DetailType": "foo_bar",
                    "Source": "Subdivisions",
                    "Detail": '{"event": "foo_bar", "datetime": '
                    '"2021-04-23T12:00:00+00:00", '
                    '"payload": {"foo": "bar"}}',
                }
            ]
        )

    def test_get_messages(self, sub_client, mocker):
        # Arrange
        mocker.patch.object(SubClient, "_prepare_subscribe")
        mocker.patch.object(SubClient, "delete_received_messages")
        boto_mock = mocker.patch.object(boto3, "client")
        boto_mock().list_queues.return_value = {
            "QueueUrls": ["pubsub_subdivisions_foo_bar"]
        }
        boto_mock().get_queue_attributes.return_value = {
            "Attributes": {"QueueArn": "foo.arn"}
        }
        message = {
            "Body": json.dumps({"Message": json.dumps({"foo": "bar"})}),
            "ReceiptHandle": "foo.one",
        }
        boto_mock().receive_message.side_effect = [{"Messages": [message]}, {}]

        # Act
        messages = sub_client.get_messages()

        # Assert
        assert messages == [{"foo": "bar"}]
        boto_mock().receive_message.assert_called_with(
            QueueUrl="pubsub_subdivisions_foo_bar", MaxNumberOfMessages=10
        )
        boto_mock().delete_message.assert_not_called()

    def test_delete_received_messages(self, sub_client, mocker):
        # Arrange
        sub_client.received_handlers = [("foo_url", "foo_receipt")]
        boto_mock = mocker.patch.object(boto3, "client")
        boto_mock().list_queues.return_value = {
            "QueueUrls": ["pubsub_subdivisions_foo_bar"]
        }

        # Act
        sub_client.delete_received_messages()

        # Assert
        boto_mock().delete_message.assert_called_with(
            QueueUrl="foo_url", ReceiptHandle="foo_receipt"
        )
