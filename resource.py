class Resource:
    def __init__(self, initial, fn=lambda x: 0):
        self.amount = initial
        self.regenerate = fn

    def update(self):
        self.amount += self.regenerate()

    def get_amount(self):
        return self.amount