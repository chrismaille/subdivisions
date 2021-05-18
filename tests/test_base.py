from enum import Enum

import pytest

from subdivisions.base import SubDivisions


class TestSubdivisions:
    @pytest.mark.parametrize(
        "name",
        [
            " Red Barchetta",
            "2112:Overture",
            2112,
            SubDivisions,
            [],
            "L1mel1ght",
            "Red Sector A",
            "XYZ",
        ],
    )
    def test_validate_bad_topic(self, name):
        test_instance = SubDivisions()
        with pytest.raises(ValueError):
            test_instance.topic = name

    @pytest.mark.parametrize("name", ["new_world_man", "Xanadu", "The_Big_Money"])
    def test_validate_good_topic(self, name):
        test_instance = SubDivisions()
        test_instance.topic = name

    def test_topic_from_enum(self):
        class Presto(Enum):
            SHOW_DONT_TELL = "Show don`t Tell"

        class CounterParts(Enum):
            COLD_FIRE = "COLD_FIRE"

        test_instance = SubDivisions()

        # Assert Bad Dog
        with pytest.raises(ValueError):
            test_instance.topic = Presto.SHOW_DONT_TELL

        # Assert Good Dog
        test_instance.topic = CounterParts.COLD_FIRE

    def test_topic_conversion(self):
        test_instance = SubDivisions()
        test_instance.topic = "FooBar"
        assert test_instance.topic == "foo_bar"
