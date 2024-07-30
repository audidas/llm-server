from typing import Callable

from app.view.conversation.sub_function.abc import Generator
from app.view.conversation.sub_function.knowledge_generator import KnowledgeGenerator
from app.view.conversation.sub_function.map_generator import MapGenerator

__map_generator = MapGenerator()
__knowledge_generator = KnowledgeGenerator()


def generator_mapper() -> Callable:
    generator_modes = {
        "map": __map_generator,
        "knowledge": __knowledge_generator,
    }

    def wrapper():
        return generator_modes

    return wrapper
