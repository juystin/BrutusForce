import sqlite3


def get_facility_ids():
    text_file = open("facility_ids.txt", "r")
    return text_file.read().splitlines()


def open_database():
    pass


def check_open_classroom(c, facility_id, time):
    classroom_is_open = False
    


facility_ids = get_facility_ids()

for facility_id in facility_ids:

