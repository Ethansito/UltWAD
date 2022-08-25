class Food:

    # This method constructs the class
    def __init__(self, name, calories: float, protein: float, fat: float, carbs: float):
        self.name = name
        self.protein = protein
        self.fat = fat
        self.carbs = carbs
        self.calories = calories

    def set_name(self, name):
        self.name = name

    def set_protein(self, protein):
        self.protein = protein

    def set_fat(self, fat):
        self.fat = fat

    def set_carbs(self, carbs):
        self.carbs = carbs

    def set_calories(self, calories):
        self.calories = calories
