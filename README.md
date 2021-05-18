# Welcome to Subdivisions

[![PyPI](https://img.shields.io/pypi/v/sub.divisions)](https://pypi.org/project/sub.divisions/)
[![Publish](https://github.com/chrismaille/subdivisions/workflows/publish/badge.svg)](https://github.com/chrismaille/subdivisions/actions)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/subdivisions)](https://www.python.org)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[AWS Eventbridge backed PubSub solution](https://www.youtube.com/watch?v=EYYdQB0mkEU)

### Install in Project

1. Install subdivisions

```shell
$ pip install sub-divisions
```

### Configure Project

1. On every project which you will send or receive messages, create a
    `pyproject.toml` with the following configuration:

```toml
[tool.subdivisions]
source_name = "ProjectName"     # For Eventbridge Schema Discovery
aws_account = ""                # AWS Account Id
aws_user = ""                   # AWS User with sufficient permissions
```

The `source_name` are used to inform the `Source` field in Eventbridge
messages. This source will be used on Eventbridge discovery schemas.

The `aws_account` is the AWS account which will be configured for
Eventbridge, KMS, SNS and SQS artifacts.

The `aws_user` is the user which we will use for create the KMS PubSub
Key. To avoid conflicts use the *AWS Secret Key* and *AWS Secret Id*
from the same user. This account must have the minimum permissions:

* Allow all Eventbridge actions
* Allow all SQS actions
* Allow all SNS actions
* Allow all KMS actions

### Usage
#### Send Messages
```python
from enum import unique, Enum
from subdivisions.client import SubClient

@unique
class MyProjectEvents(Enum):
    MY_EXAMPLE_EVENT = "my_example_event"

client = SubClient()
client.topic = MyProjectEvents.MY_EXAMPLE_EVENT
client.send({"foo": "bar"})
```

#### Receive Messages
```python
from enum import unique, Enum
from subdivisions.client import SubClient

@unique
class MyProjectEvents(Enum):
    MY_EXAMPLE_EVENT = "my_example_event"

client = SubClient()
client.topic = MyProjectEvents.MY_EXAMPLE_EVENT
messages = client.get_messages()    # use the ``from_dead_letter=True` to receive Dead Letter messages
# Process messages
client.delete_received_messages()
```
### AWS Credentials

Subdivisions will use AWS default environment variables. If you need to define another credentials, use the following variables:

```env
SUBDIVISIONS_USE_AWS_ENV_VARS="false"
SUBDIVISIONS_AWS_ACCESS_KEY_ID="your id"
SUBDIVISIONS_AWS_SECRET_ACCESS_KEY="your key"
SUBDIVISIONS_AWS_SESSION_TOKEN="your token" # optional
```

### Configuration

Configure subdivisions options in `pyproject.toml` file, inside `[tool.subdivisions]` table:

```toml
# pyproject.toml
[tool.subdivisions]
aws_region = "us-east-1"            # AWS Region
aws_account = ""                    # AWS Account for configuration/use
aws_user = ""                       # AWS User with sufficient permissions
aws_sqs_policy = ""                 # AWS SQS Policy (default in policies.py)
aws_sns_policy = ""                 # AWS SNS Policy (default in policies.py)
aws_kms_policy = ""                 # AWS KMS Policy (default in policies.py)
pub_key = "PubSubKey"               # KMS PubSubKey (must be created first)
sqs_tags = []                       # SQS tags for new queues. Example [{"foo": "bar"}]
queue_prefix = ""                   # Prefix for new SQS queues
queue_suffix = ""                   # Suffix for new SQS queues
queue_max_receive_count = 1000      # SQS MaxReceiveCount setting
sns_prefix = ""                     # Prefix for new SNS topics
sns_suffix = ""                     # Suffix for new SNS topics
sns_tags = []                       # SNS tags for new topics. Example [{"foo": "bar"}]
event_prefix = ""                   # Prefix for new Eventbride rules
event_suffix = ""                   # Suffix for new Eventbride rules
event_tags = []                     # Eventbridge tags for new rules. Example [{"foo": "bar"}]
event_bus = "default"               # Eventbridge Bus
source_name = ""                    # Eventbridge default source name. No default, must inform
auto_create_new_topic = true        # Auto create new topic if not exists in Eventbridge
auto_remove_from_queue = false      # Acknowledge first messages on receive
use_aws_env_vars = true             # Use AWS default env vars. If false append "SUBDIVISION_" on env vars. Example: "SUBDIVISION_AWS_ACCESS_KEY_ID"
default_prefix = "pubsub"           # Default prefix for all sns, sqs and rule created
default_suffix = ""                 # Default suffix for all sns, sqs and rule created
```

All options above can be configured in environment variables. Just append `SUBDIVISIONS_` on name. Example: `SUBDIVISIONS_SOURCE_NAME="my_project"`
