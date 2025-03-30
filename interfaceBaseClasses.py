
from abc import ABC, abstractmethod;    


class InterfaceBaseClass(ABC):

    @staticmethod
    @abstractmethod
    def get_human_readable_name() -> str:
        raise NotImplementedError;

    @abstractmethod
    def process(self, input):
        raise NotImplementedError



