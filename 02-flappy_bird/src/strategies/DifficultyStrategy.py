from abc import ABC, abstractmethod

from gale.input_handler import InputData

class DifficultyStrategy(ABC):
    @abstractmethod
    def update_world(self, world, dt: float) -> None:
        pass

    @abstractmethod
    def update_bird(self, bird, dt: float) -> None:
        pass

    @abstractmethod
    def handle_bird_input(self, bird, input_id: str, input_data: InputData) -> None:
        pass

