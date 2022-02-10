from selenium import webdriver
import os

# Executable path of browser driver.
PATH = os.getcwd() + "\chromedriver.exe"

# Website link to Ohio State's Room Matrix.
ROOM_MATRIX_LINK = "https://courses.osu.edu/psp/csosuct/EMPLOYEE/PUB/c/OSR_CUSTOM_MENU.OSR_ROOM_MATRIX.GBL?"

# Create Driver object with browser driver.
driver = webdriver.Chrome(PATH)

# Open website.
driver.get(ROOM_MATRIX_LINK)

# TODO: Grab class time data.

# Close website.
driver.quit()