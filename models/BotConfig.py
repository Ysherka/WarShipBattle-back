from dataclasses import dataclass


@dataclass
class BotConfig:
    name: str = "Bot"
    difficulty: int = 1
    field_size: int = 10
