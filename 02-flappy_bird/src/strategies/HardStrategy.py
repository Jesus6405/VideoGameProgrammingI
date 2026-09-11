from .DifficultyStrategy import DifficultyStrategy
import random
import settings

class HardStrategy(DifficultyStrategy):
    def __init__(self):
        self.move_left = False
        self.move_right = False
        self.horizontal_speed = settings.HARD_MODE_HORIZONTAL_SPEED
        self.next_spawn_time = random.uniform(1.2, 2.2)

    def update_world(self, world, dt: float) -> None:
        if world.generate_logs: 
            world.logs_spawn_timer += dt
            world.power_up_spawn_timer += dt

            if world.logs_spawn_timer >= self.next_spawn_time:
                world.logs_spawn_timer = 0.0
                max_vertical_delta = min(80.0, self.next_spawn_time * 50.0)
                height_offset = random.uniform(-max_vertical_delta, max_vertical_delta)

                y = max (-settings.LOG_HEIGHT + 10, min(world.last_log_y + height_offset, settings.VIRTUAL_HEIGHT - 125 - settings.LOG_HEIGHT))

                world.last_log_y = y

                if random.random() < 0.3:
                    world.logs.append(world.log_pair_factory.create(settings.VIRTUAL_WIDTH, y, {"closes" : True}))
                else:
                    world.logs.append(world.log_pair_factory.create(settings.VIRTUAL_WIDTH, y))
                
                self.next_spawn_time = random.uniform(1.2, 2.2)

            if world.power_up_spawn_timer >= world.next_powerup_spawn and world.logs_spawn_timer >= (0.6*self.next_spawn_time):
                world.power_up_spawn_timer = 0.0
                world.next_powerup_spawn = random.uniform(10.0, 18.0)
            
                y = random.randint(30, settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT - 40)
                world.power_ups.append(world.ghost_power_up_factory.create(settings.VIRTUAL_WIDTH, y))

            

    def handle_bird_input(self, bird, input_id: str, input_data) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()
        if input_id == "move_left":
            if input_data.pressed:
                self.move_left = True
            elif input_data.released:
                self.move_left = False
        if input_id == "move_right":
            if input_data.pressed:
                self.move_right = True
            elif input_data.released:
                self.move_right = False

    def update_bird(self, bird, dt: float) -> None:
        bird.update(dt)

        if self.move_left:
            bird.x -= self.horizontal_speed * dt
        if self.move_right:
            bird.x += self.horizontal_speed * dt

        bird.x = max(0, min(bird.x, settings.VIRTUAL_WIDTH - bird.width))

        
