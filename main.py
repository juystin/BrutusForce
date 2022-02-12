from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# Executable path of browser driver.
PATH = os.getcwd() + "\chromedriver.exe"

# Link to Ohio State's Room Matrix.
ROOM_MATRIX_LINK = "https://courses.osu.edu/psc/csosuct/EMPLOYEE/PUB/c/OSR_CUSTOM_MENU.OSR_ROOM_MATRIX.GBL?PortalActualURL=https%3a%2f%2fcourses.osu.edu%2fpsc%2fcsosuct%2fEMPLOYEE%2fPUB%2fc%2fOSR_CUSTOM_MENU.OSR_ROOM_MATRIX.GBL&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fcourses.osu.edu%2fpsp%2fcsosuct%2f&PortalURI=https%3a%2f%2fcourses.osu.edu%2fpsc%2fcsosuct%2f&PortalHostNode=CAMP&NoCrumbs=yes&PortalKeyStruct=yes"

# Create Driver object with browser driver.
driver = webdriver.Chrome(PATH)

# Open website.
driver.get(ROOM_MATRIX_LINK)

# Find room search bar and enter room number.
search_bar = driver.find_element(By.ID, "OSR_DERIVED_RM_FACILITY_ID")
search_bar.send_keys("CL0277")
search_bar.send_keys(Keys.RETURN)

time.sleep(1)

# Refresh schedule.
refresh_button = driver.find_element(By.ID, "DERIVED_CLASS_S_SSR_REFRESH_CAL")
refresh_button.click()

time.sleep(3)

# Grabs each individual time box.
time_boxes = driver.find_elements(By.CLASS_NAME, "PSLEVEL3GRIDODDROW")
raw_class_info = []

# Current box being looked at.
current_box = 1

# Bruh.
days_in_week = 7

# Tracks the amount of hours left for each class.
class_tracker = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 0: 0}

for element in time_boxes:

    # IS THIS NECESSARY?
    #
    # # OSU's Room Matrix grid system performs in a fashion such that class times override the number of boxes
    # # in each row. Essentially, no class will be counted twice.
    # # Because of this, there are not actually 7 boxes (representing 7 days) for each row.
    #
    # # Catch current_box up to the actual day. (Fixes the problem explained above.)
    # while class_tracker[current_box % days_in_week] > 0:
    #     class_tracker[current_box % days_in_week] = class_tracker[current_box % days_in_week] - 1
    #     current_box = current_box + 1
    #
    #     # If incrementing makes the day Saturday, push to Monday.
    #     if (current_box % days_in_week == 6):
    #         current_box = current_box + 2

    # Tries to filter out other crap other than class information.
    # Note that the "tub" of elements are the elements in the class of "PSLEVEL3GRIDODDROW".
    # For future updates, try to improve upon this.

    if (element.text[0:1].isalpha()) and (element.text[0:3].isupper()):
        element_separated = element.text.splitlines()[0:4]

        if current_box % days_in_week == 1:
            raw_class_info.append("Monday")
        elif current_box % days_in_week == 2:
            raw_class_info.append("Tuesday")
        elif current_box % days_in_week == 3:
            raw_class_info.append("Wednesday")
        elif current_box % days_in_week == 4:
            raw_class_info.append("Thursday")
        elif current_box % days_in_week == 5:
            raw_class_info.append("Friday")
        elif current_box % days_in_week == 6:
            raw_class_info.append("Saturday")
        elif current_box % days_in_week == 0:
            raw_class_info.append("Sunday")

        class_tracker[current_box % days_in_week] = 5

        for word in element_separated:
            raw_class_info.append(word)

    # TODO: FIX DAY TRACKER
    # # Increment current_box only when looking at top of a class timeslot or at an empty timeslot.
    # if (element.text[0:1].isalpha()) and (element.text[0:3].isupper()):
    #     current_box = current_box + 1
    #
    #     # If incrementing makes the day Saturday, push to Monday.
    #     if (current_box % days_in_week == 6):
    #         current_box = current_box + 3

# Create a list of dictionaries, which hold class information.
weekly_schedule = []

currentIndex = 0
while currentIndex < len(raw_class_info):
    if raw_class_info[currentIndex][0:1].isalpha():
        class_day = raw_class_info[currentIndex]
        class_number = raw_class_info[currentIndex + 1]
        class_type = raw_class_info[currentIndex + 2]
        class_duration = raw_class_info[currentIndex + 3]
        class_location = raw_class_info[currentIndex + 4]
        class_info = {"Day": class_day, "Class": class_number, "Type": class_type, "Duration": class_duration,
                      "Location": class_location}
        weekly_schedule.append(class_info)
        currentIndex = currentIndex + 4
    currentIndex = currentIndex + 1

for single_class in weekly_schedule:
    print(single_class)

# Close website.
# driver.quit()
