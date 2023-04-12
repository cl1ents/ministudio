from pygame import Vector2

class Behaviour:
    def __init__(self, app):
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.rotation = 0
        
    def update(self, app):
        self.velocity *= max(1-app.deltaTime, 0)
        self.position += self.velocity*app.deltaTime
    
    def render(self, app):
        pass