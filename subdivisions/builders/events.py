import json
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

import stringcase
from loguru import logger

from subdivisions.builders import SubDivisionsBuilder
from subdivisions.config import sub_config


@dataclass
class SubDivisionsEventsBuilder(SubDivisionsBuilder):
    event_rule_arn: Optional[str] = None
    active_rules: Optional[List[Dict[Any, Any]]] = None
    best_match: Optional[str] = None

    @property
    def event_name(self):
        suffix = (
            sub_config.event_suffix
            if sub_config.event_suffix
            else sub_config.default_suffix
        )
        return stringcase.titlecase(
            f"{sub_config.event_prefix or sub_config.default_prefix}"
            f"{stringcase.titlecase(self.topic)}"
            f"{suffix}"
        ).replace(" ", "")

    def put_rule(self):

        event_pattern = json.dumps(
            {"detail-type": [self.topic], "detail": {"event": [self.topic]}}
        )

        put_rules_arguments = {
            "Name": self.event_name,
            "EventPattern": event_pattern,
            "State": "ENABLED",
            "Description": f"Created in {sub_config.source_name} for "
            f"{stringcase.titlecase(self.event_name)} events",
            "EventBusName": sub_config.event_bus,
        }
        if sub_config.sns_tags:
            put_rules_arguments["Tags"] = (sub_config.sns_tags,)

        put_event_response = self.get_client("events").put_rule(**put_rules_arguments)
        logger.debug(f"Event Create/Update Response is: {put_event_response}")
        rule_arn = put_event_response["RuleArn"]
        return rule_arn

    def put_target(self, sns_topic_arn: str):
        put_target_response = self.get_client("events").put_targets(
            Rule=self.event_name,
            Targets=[
                {"Id": self.event_name, "Arn": sns_topic_arn, "InputPath": "$.detail"}
            ],
        )
        logger.debug(f"Put Target Response is: {put_target_response}")

    def topic_exists(self) -> bool:
        response = self.get_client("events").list_rules(Limit=100)
        self.active_rules = [
            rule for rule in response["Rules"] if rule["State"] == "ENABLED"
        ]
        topic_found = [
            rule for rule in self.active_rules if rule["Name"] == self.event_name
        ]
        return len(topic_found) > 0

    def similar_topic_exists(self) -> bool:
        if not self.active_rules:
            return False
        similar_topics = [
            (
                rule["Name"],
                SequenceMatcher(
                    None, self.event_name, rule["Name"], autojunk=True
                ).ratio(),
            )
            for rule in self.active_rules
            if SequenceMatcher(
                None, self.event_name, rule["Name"], autojunk=True
            ).ratio()
            > 0.80
        ]
        if len(similar_topics) == 0:
            return False
        similar_topics.sort(reverse=True, key=lambda x: x[1])
        self.best_match = similar_topics[0][0]
        return True
