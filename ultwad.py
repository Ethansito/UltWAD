import datetime

import pandas as pd
from os.path import exists
from food import Food

# Program Startup
# If the data file exists, try to read the file. If the file is empty or does not exist, create a basic dataframe.
if exists("core_data.xlsx"):
    try:
        core_data = pd.read_excel("core_data.xlsx", sheet_name="core_data", index_col=0)
        day_list = list(core_data.index.values)
        weight_goal = core_data.at[day_list[0], "Weight Goal"]
        calorie_goal = core_data.at[day_list[0], "Calorie Goal"]
        protein_goal = core_data.at[day_list[0], "Protein Goal"]
        fat_goal = core_data.at[day_list[0], "Fat Goal"]
        carbs_goal = core_data.at[day_list[0], "Carbs Goal"]
    except (ValueError, IndexError) as e:
        print("core_data is empty")
        core_data = pd.DataFrame(columns=["Weight", "Calories", "Protein", "Fat", "Carbs",
                                          "Weight Goal", "Calorie Goal", "Protein Goal", "Fat Goal", "Carbs Goal"])
        day_list = list(core_data.index.values)
        weight_goal = 1
        calorie_goal = 1
        protein_goal = 1
        fat_goal = 1
        carbs_goal = 1
else:
    core_data = pd.DataFrame(columns=["Weight", "Calories", "Protein", "Fat", "Carbs",
                                      "Weight Goal", "Calorie Goal", "Protein Goal", "Fat Goal", "Carbs Goal"])
    day_list = list(core_data.index.values)
    weight_goal = 1
    calorie_goal = 1
    protein_goal = 1
    fat_goal = 1
    carbs_goal = 1

if exists("core_data.xlsx"):
    try:
        food_registry = pd.read_excel("core_data.xlsx", sheet_name="food_registry", index_col=0)
        food_list = list(food_registry.index.values)
        # Construct a list of food objects based on the Excel data
        # Instead of editing the dataframes, we will edit the objects in the list and return them to dataframes
        # when the program shuts down.
        food_objects = []
        for item in food_list:
            load_food = Food(item, food_registry.at[item, "Calories"], food_registry.at[item, "Protein"],
                             food_registry.at[item, "Fat"], food_registry.at[item, "Carbs"])
            food_objects.append(load_food)

    except ValueError:
        print("food_registry is empty")
        food_registry = pd.DataFrame(columns=["Calories", "Protein", "Fat", "Carbs"])
        food_list = list(food_registry.index.values)
        food_objects = []

else:
    food_registry = pd.DataFrame(columns=["Calories", "Protein", "Fat", "Carbs"])
    food_list = list(food_registry.index.values)
    food_objects = []

# Main loop
running = True
while running:
    command = input("""Command: """).lower()
    command = command.split(" ")

    # Register food item
    if command[0] == "food" and command[1] == "add":
        registering = True
        while registering:
            name = input("Name: ")
            calories = float(input("Calories: "))
            protein = float(input("Protein: "))
            fat = float(input("Fat: "))
            carbs = float(input("Carbs: "))
            new_food = Food(name, calories, protein, fat, carbs)
            food_objects.append(new_food)
            print("Food registered!")
            registering = False
    # Add day to core_data
    elif command[0] == "day" and command[1] == "add":
        registering = True
        date = ""
        while registering:
            today = input("Creating today? (Y/N): ")
            if today.lower() == "y":
                date = str(datetime.date.today())
                registering = False
            elif today.lower() == "n":
                date = str(input("Date (YYYY-MM-DD): "))
                registering = False
            else:
                print("Invalid command.")

        weight = input("Weight: ")

        registering = True
        # These variables will be used to count the macros for the day.
        day_calories = 0
        day_protein = 0
        day_fat = 0
        day_carbs = 0
        while registering:
            entry = input("Food and Servings (Name #): ")
            entry = entry.split()
            # If the food input matches a registered food item, add its macros according to # number of servings to the
            # day's count.
            item: Food
            for item in food_objects:
                if entry[0] == item.name:
                    day_calories += item.calories * float(entry[1])
                    day_protein += item.protein * float(entry[1])
                    day_fat += item.fat * float(entry[1])
                    day_carbs += item.carbs * float(entry[1])
            if entry[0].lower() == "quit":
                # Once the user is done creating the day, update the core_data DataFrame with the new day's info.
                assembler = [[weight, day_calories, day_protein, day_fat, day_carbs]]
                day_data = pd.DataFrame(assembler, index=[date],
                                        columns=["Weight", "Calories", "Protein", "Fat", "Carbs"])
                core_data = pd.concat([core_data, day_data])
                day_list.append(date)
                registering = False
                break

    # Add a fitness/diet goal
    elif command[0] == "goal" and command[1] == "add":
        pass

    # Data Analysis
    # This area of the program is where we will be making the charts from the recorded data.

    elif command[0] == "quit":
        running = False
    else:
        print("Invalid command.")

# Program Shutdown
# Creating new dataframe to replace old one
index = []
assembler = []
for item in food_objects:
    # Add item name to list of rows
    index.append(item.name)
    # Use the other parameters of the item to build the rest of the row.
    build = [item.calories, item.protein, item.fat, item.calories]
    assembler.append(build)
# Set goals to core_data before exporting
# This may be moved to the "goal add" and "goal edit" sections
try:
    core_data.at[day_list[0], "Weight Goal"] = weight_goal
    core_data.at[day_list[0], "Calorie Goal"] = calorie_goal
    core_data.at[day_list[0], "Protein Goal"] = protein_goal
    core_data.at[day_list[0], "Fat Goal"] = fat_goal
    core_data.at[day_list[0], "Carbs Goal"] = carbs_goal
except IndexError:
    print("core_data empty")
# Reassign food registry DataFrame before exporting
food_registry = pd.DataFrame(assembler, index=index, columns=["Calories", "Protein", "Fat", "Carbs"])
# Exporting everything to Excel
with pd.ExcelWriter("core_data.xlsx") as writer:
    core_data.to_excel(writer, sheet_name="core_data")
    food_registry.to_excel(writer, sheet_name="food_registry")
