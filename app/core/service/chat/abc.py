from abc import ABC, abstractmethod


class ChatUseCae(ABC):

    @abstractmethod
    def chat(self, *args, **kwargs):
        pass

    @abstractmethod
    def first_chat(self, *args, **kwargs):
        pass
