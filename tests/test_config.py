from subdivisions.config import SubDivisionConfig


class TestSubDivisionConfig:
    def test_get_from_env_or_settings(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("SUBDIVISIONS_AUTO_REMOVE_FROM_QUEUE", "true")

        # Act
        test_config = SubDivisionConfig.get_config()

        # Assert
        assert test_config.auto_remove_from_queue is True
        monkeypatch.delenv("SUBDIVISIONS_AUTO_REMOVE_FROM_QUEUE")
