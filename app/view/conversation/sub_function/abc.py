from abc import ABC, abstractmethod
from typing import Optional

from pydantic import UUID4


class Generator(ABC):

    @abstractmethod
    def generate(
                self,
                conversation_id: UUID4,
                parent_id: UUID4,
                model: str,
                root_id: Optional[UUID4] = None,
                *args,
                **kwargs
    ):
        pass

    @abstractmethod
    def first_generate(
            self,
            conversation_id: UUID4,
            parent_id: UUID4,
            root_id: Optional[UUID4] = None,
            *args,
            **kwargs
    ):
        pass
