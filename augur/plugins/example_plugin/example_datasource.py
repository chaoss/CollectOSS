class ExampleDatasource:
    def __init__(self):
        self.counter = 0

    def hello_world(self, add=1):
        self.counter += add
        return {'counter': add}