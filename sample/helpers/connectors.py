import os
import sqlite3

from selenium import webdriver

INPUT_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "building_numbers.txt")
DATABASE_NAME = "brutusforce.db"
DRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver")

def load_building_numbers():
    with open(INPUT_FILE_PATH) as f:
        lines = [line.rstrip() for line in f]
    return lines

def create_connection():
    return sqlite3.connect(DATABASE_NAME)

def create_driver():
    return webdriver.Chrome(DRIVER_PATH)