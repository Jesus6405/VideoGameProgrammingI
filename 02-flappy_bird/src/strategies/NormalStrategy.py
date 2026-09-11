from .DifficultyStrategy import DifficultyStrategy
import random 
from gale.input_handler import InputData
import settings 

class NormalStrategy(DifficultyStrategy):
    def update_world(self, world, dt: float) -> None:
        if world.generate_logs:
            world.logs_spawn_timer += dt
        
            if world.logs_spawn_timer >= settings.TIME_TO_SPAWN_LOGS:
                world.logs_spawn_timer = 0.0
                y = max(-settings.LOG_HEIGHT + 10, min(world.last_log_y + random.randint(-20, 20), settings.VIRTUAL_HEIGHT - 115 - settings.LOG_HEIGHT))
                world.last_log_y = y
                world.logs.append(world.log_pair_factory.create(settings.VIRTUAL_WIDTH, y))

    def update_bird(self, bird, dt: float) -> None:
        bird.update(dt)

    def handle_bird_input(self, bird, input_id: str, input_data: InputData) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()