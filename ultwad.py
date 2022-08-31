import datetime


import pandas as pd
from os.path import exists
from food import Food
from matplotlib import pyplot as plt

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

# Establishing today's date for future reference.
date1 = str(datetime.date.today())

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
        while registering:
            today = input("Creating today? (Y/N): ")
            if today.lower() == "y":
                registering = False
            elif today.lower() == "n":
                date1 = str(input("Date (YYYY-MM-DD): "))
                registering = False
            else:
                print("Invalid command.")

        weight = float(input("Weight: "))

        registering = True
        # These variables will be used to count the macros for the day.
        day_calories = 0
        day_protein = 0
        day_fat = 0
        day_carbs = 0
        while registering:
            entry = input("Food and Servings (Name #): ")
            entry = entry.split()
            entry_len = len(entry)
            try:
                servings = float(entry[entry_len-1])
                entry.remove(entry[entry_len-1])
                entry = " ".join(entry)
                # If the food input matches a registered food item,
                # add its macros according to # number of servings to the day's count.
                item: Food
                for item in food_objects:
                    if entry == item.name:
                        day_calories += item.calories * servings
                        day_protein += item.protein * servings
                        day_fat += item.fat * servings
                        day_carbs += item.carbs * servings
            except ValueError:
                if entry[0].lower() == "quit":
                    # Once the user is done creating the day, update the core_data DataFrame with the new day's info.
                    assembler = [[weight, day_calories, day_protein, day_fat, day_carbs]]
                    day_data = pd.DataFrame(assembler, index=[date1],
                                            columns=["Weight", "Calories", "Protein", "Fat", "Carbs"])
                    core_data = pd.concat([core_data, day_data])
                    day_list.append(date1)
                    registering = False
                    print("Day Created!")
                    break
                else:
                    print("ERROR: Final input must be numerical.")

    # Set a fitness/diet goal
    elif command[0] == "goal" and command[1] == "set":
        setting_goal = True
        while setting_goal:
            goal = input(""""Which goal would you like to set?
            (1) Weight Goal
            (2) Calorie Goal
            (3) Protein Goal
            (4) Fat Goal
            (5) Carbs Goal
            """)
            if goal.lower() == "1":
                set_goal = input("Weight Goal: ")
                weight_goal = float(set_goal)
            elif goal.lower() == "2":
                set_goal = input("Calorie Goal: ")
                calorie_goal = float(set_goal)
            elif goal.lower() == "3":
                set_goal = input("Protein Goal: ")
                protein_goal = float(set_goal)
            elif goal.lower() == "4":
                set_goal = input("Fat Goal: ")
                fat_goal = float(set_goal)
            elif goal.lower() == "5":
                set_goal = input("Carbs Goal: ")
                carbs_goal = float(set_goal)
            elif goal.lower() == "quit":
                setting_goal = False
                break

    # Data Analysis
    # This area of the program is where we will be making the charts from the recorded data.
    elif command[0] == "analysis":
        analyzing = True
        while analyzing:
            choice = input("""Which analysis would you like?
            (1) Goals vs Data over time (line chart)
            (2) Macro distribution (pie chart)
            (3) The whole shebang
            """)

            # Because the program allows users to input data for previous or future dates, the dates can be out
            # of order if you just plot the dates directly from core_data. Instead, we need to get the dates
            # and sort them chronologically, then plot the sorted list.
            day_list.sort(key=lambda date: datetime.datetime.strptime(date, '%Y-%m-%d'))
            print(day_list)
            # Now we have to reconnect the values with the sorted dates.
            # Otherwise, the data will still be out of order.
            weight_list = []
            calorie_list = []
            protein_list = []
            fat_list = []
            carbs_list = []
            for day in day_list:
                weight_list.append(core_data.at[day, "Weight"])
                calorie_list.append(core_data.at[day, "Calories"])
                protein_list.append(core_data.at[day, "Protein"])
                fat_list.append(core_data.at[day, "Fat"])
                carbs_list.append(core_data.at[day, "Carbs"])

            # Line Chart
            if choice.lower() == "1":
                # Unpacking the subplots from their list into variables. The tuples are used to inform the program
                # which item in the list should be assigned to which variable.
                fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(nrows=3, ncols=2)
                # Weight Subplot
                ax1.plot(day_list, weight_list, label="Weight")
                ax1.axhline(y=weight_goal, label="Weight Goal", color="#f07f08")
                ax1.legend()
                ax1.set_title("Weight vs Weight Goal")
                ax1.set_ylabel("Weight")
                # Calories Subplot
                ax3.plot(day_list, calorie_list, label="Calories")
                ax3.axhline(y=calorie_goal, label="Calorie Goal", color="#f07f08")
                ax3.legend()
                ax3.set_title("Calories Eaten vs Goal over Time")
                ax3.set_ylabel("Calories")
                # Protein Subplot
                ax4.plot(day_list, protein_list, label="Protein")
                ax4.axhline(y=calorie_goal, label="Protein Goal", color="#f07f08")
                ax4.legend()
                ax4.set_title("Protein Eaten vs Goal over Time")
                ax4.set_ylabel("Protein (g)")
                # Fat Subplot
                ax5.plot(day_list, fat_list, label="Fat")
                ax5.axhline(y=fat_goal, label="Fat Goal", color="#f07f08")
                ax5.legend()
                ax5.set_title("Fat Eaten vs Goal over Time")
                ax5.set_xlabel("Days")
                ax5.set_ylabel("Fat (g)")
                # Carbs Subplot
                ax6.plot(day_list, carbs_list, label="Carbs")
                ax6.axhline(y=carbs_goal, label="Carbs Goal", color="#f07f08")
                ax6.legend()
                ax6.set_title("Carbs Eaten vs Goal over Time")
                ax6.set_xlabel("Days")
                ax6.set_ylabel("Carbs (g)")

                # There is an empty subplot, so we will make it invisible
                ax2.set_visible(False)

                plt.show()

            elif choice.lower() == "2":
                fig, (ax2, ax) = plt.subplots(2, 1)
                # Stacked Area Chart
                # A stacked area chart will allow us to show
                # the way our macros are distributed across the calories we eat.
                ax.stackplot(day_list, protein_list, fat_list, carbs_list,
                             labels=["Protein (g)", "Fat (g)", "Carbs (g)"])
                ax.set_title("Macro Distribution over Time")
                ax.legend()

                # Pie Chart
                # For showing today's macro distribution
                pie_list = [core_data.at[date1, "Protein"], core_data.at[date1, "Fat"], core_data.at[date1, "Carbs"]]
                ax2.pie(pie_list, labels=["Protein", "Fat", "Carbs"], autopct="%.2f%%")
                ax2.set_title("Macro Distribution Today")

                plt.show()

            # For this option, I copy-pasted the code from the two other options with a couple small changes to make
            # everything coexist.
            elif choice.lower() == "3":
                line, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(nrows=3, ncols=2)
                ax1.plot(day_list, weight_list, label="Weight")
                ax1.axhline(y=weight_goal, label="Weight Goal", color="#f07f08")
                ax1.legend()
                ax1.set_title("Weight vs Weight Goal")
                ax1.set_ylabel("Weight")
                ax3.plot(day_list, calorie_list, label="Calories")
                ax3.axhline(y=calorie_goal, label="Calorie Goal", color="#f07f08")
                ax3.legend()
                ax3.set_title("Calories Eaten vs Goal over Time")
                ax3.set_ylabel("Calories")
                ax4.plot(day_list, protein_list, label="Protein")
                ax4.axhline(y=calorie_goal, label="Protein Goal", color="#f07f08")
                ax4.legend()
                ax4.set_title("Protein Eaten vs Goal over Time")
                ax4.set_ylabel("Protein (g)")
                ax5.plot(day_list, fat_list, label="Fat")
                ax5.axhline(y=fat_goal, label="Fat Goal", color="#f07f08")
                ax5.legend()
                ax5.set_title("Fat Eaten vs Goal over Time")
                ax5.set_xlabel("Days")
                ax5.set_ylabel("Fat (g)")
                ax6.plot(day_list, carbs_list, label="Carbs")
                ax6.axhline(y=carbs_goal, label="Carbs Goal", color="#f07f08")
                ax6.legend()
                ax6.set_title("Carbs Eaten vs Goal over Time")
                ax6.set_xlabel("Days")
                ax6.set_ylabel("Carbs (g)")
                ax2.set_visible(False)
                pie, (ax2, ax) = plt.subplots(2, 1)
                ax.stackplot(day_list, protein_list, fat_list, carbs_list,
                             labels=["Protein (g)", "Fat (g)", "Carbs (g)"])
                ax.set_title("Macro Distribution over Time")
                ax.legend()
                pie_list = [core_data.at[date1, "Protein"], core_data.at[date1, "Fat"], core_data.at[date1, "Carbs"]]
                ax2.pie(pie_list, labels=["Protein", "Fat", "Carbs"], autopct="%.2f%%")
                ax2.set_title("Macro Distribution Today")

                plt.show()

            elif choice.lower() == "quit":
                analyzing = False
                break
            else:
                print("Invalid Command")

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
    build = [item.calories, item.protein, item.fat, item.carbs]
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
    print("Core_data empty. You must add your first day before setting goals.")
# Reassign food registry DataFrame before exporting
food_registry = pd.DataFrame(assembler, index=index, columns=["Calories", "Protein", "Fat", "Carbs"])
# Exporting everything to Excel
with pd.ExcelWriter("core_data.xlsx") as writer:
    core_data.to_excel(writer, sheet_name="core_data")
    food_registry.to_excel(writer, sheet_name="food_registry")
