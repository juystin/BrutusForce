from sample.helpers.get_buildings import populate_building_tables
from sample.helpers.get_classes import populate_classes_table

user_input = input("Repopulate buildings/classrooms? (Y/N): ")

if (user_input == "Y"):
    print("Beginning to populate building and classroom tables...")
    populate_building_tables()
    print("Populate building and classroom tables successful.")

print("Beginning to populate classes table...")
populate_classes_table()
print("Populate classes table successful.")
