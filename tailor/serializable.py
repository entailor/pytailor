from abc import ABC, abstractmethod


class Serializable(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        return NotImplemented

    @classmethod
    @abstractmethod
    def from_dict(cls, d: dict) -> 'Serializable':
        return NotImplemented
