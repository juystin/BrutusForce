from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import time
import sqlite3


def get_facility_ids():
    text_file = open("facility_ids.txt", "r")
    return text_file.read().splitlines()
    

def create_driver(path):
    return webdriver.Chrome(path)


def open_website(webdriver, link):
    webdriver.get(link)


def search_classroom(driver, room_num):
    search_bar = driver.find_element(By.ID, "OSR_DERIVED_RM_FACILITY_ID")

    # Make sure text field is empty.
    search_bar.send_keys(Keys.CONTROL, 'a')
    search_bar.send_keys(Keys.BACKSPACE)

    search_bar.send_keys(room_num)
    search_bar.send_keys(Keys.RETURN)


def refresh_schedule(driver):
    refresh_button = driver.find_element(By.ID, "DERIVED_CLASS_S_SSR_REFRESH_CAL")
    refresh_button.click()


def grab_box_info(driver, By, filter):
    return driver.find_elements(By, filter)


def parse_box_data(time_boxes):

    # Currently, ''time_boxes'' contains all elements in the class "PSLEVEL3GRIDODDROW".
    # (Filtering algorithm subject to change in the future)

    # Always ignore first nine (nine) elements.
    # These elements consist of *the entire grid*, the *"Time" box*, and *the names and dates of the seven-day time span*,
    # which are irrelevant (as of now).
    time_boxes = time_boxes[9:]

    # OSU's Room Matrix grid system performs in a fashion such that class times override the number of boxes
    # in each row. Essentially, no class will be counted twice.
    # Because of this, there are not actually 7 boxes (representing 7 days) for each row.

    # To circumvent above issues, we use our own counter variable that tracks the amount of boxes. We effectively cut the
    # class times into separate boxes, so each row will hold 7 boxes.
    # We also have a tracker that tells us the height of each box (class duration).
    time_left_of_class = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 0: 0}
    boxes_per_row = 7
    current_box = 1

    # Store class information in separate dictionaries.
    classes_information = []

    for time_box in time_boxes:

        # At this point, ''time_box'' is either:
        # - an empty timeslot box
        # - the top of a class info box
        # - an hourly box

        # If class info box, grab class info.
        if (time_box.text[0:1].isalpha()) and (time_box.text[0:3].isupper()):

            # Separate text into 4 strings: class number, class type, class duration, class location.
            element_separated = time_box.text.splitlines()[0:4]
            # Calculate day.
            if current_box % boxes_per_row == 1:
                day = "Monday"
            elif current_box % boxes_per_row == 2:
                day = "Tuesday"
            elif current_box % boxes_per_row == 3:
                day = "Wednesday"
            elif current_box % boxes_per_row == 4:
                day = "Thursday"
            elif current_box % boxes_per_row == 5:
                day = "Friday"

            # Create dictionary with class information.
            info = {
                "Day": day,
                "Class Number": element_separated[0],
                "Class Type": element_separated[1],
                "Class Start": convert_to_24_hr(element_separated[2][0:7]),
                "Class End": convert_to_24_hr(element_separated[2][9:]),
                "Class Location": element_separated[3],
            }

            classes_information.append(info)
            # This box will not be recounted in CONSEQUENT rows. Store the (height of this box - 1) to know how
            # many iterations to make up for.
            time_left_of_class[current_box % boxes_per_row] = int(time_box.get_attribute("rowspan")) - 1

        # Increment ''current_box'' ONLY when not the extra element (denoted by first character being a digit)
        if not time_box.text[0:1].isdigit():
            current_box = current_box + 1

            # Increment current_box to the next empty time or hourly box.
            while time_left_of_class[current_box % boxes_per_row] > 0:
                time_left_of_class[current_box % boxes_per_row] = time_left_of_class[current_box % boxes_per_row] - 1
                current_box = current_box + 1

    return classes_information


def convert_to_24_hr(time):
    # First, make sure is in ##:##XX format.
    if (time[1] == ":"):
        time = "0" + time

    # If PM, add 12 hours, except if 12:##.
    if (time[0:2] != "12") and (time[5:7] == "PM"):
        fixed_time = str(int(time[0:2]) + 12) + time[2:-2]
    else:
        fixed_time = time[0:-2]

    # Lazy fix for extra letter at end. Will be updated.
    if (fixed_time[-1:].isalpha()):
        fixed_time = fixed_time[0:-1]

    return fixed_time


def output_info(c, facility_id, weekly_schedule):

    for class_info in weekly_schedule:
        c.execute("INSERT INTO classes VALUES (?,?,?,?,?,?,?,?)", (facility_id, class_info["Class Location"],
                  class_info["Day"], class_info["Class Number"],
                  class_info["Class Start"][0:2], class_info["Class Start"][3:5],
                  class_info["Class End"][0:2], class_info["Class End"][3:5]))

    conn.commit()

# Executable path of browser driver.
DRIVER_PATH = os.getcwd() + "\chromedriver.exe"

# Link to Ohio State's Room Matrix.
ROOM_MATRIX_LINK = "https://courses.osu.edu/psc/csosuct/EMPLOYEE/PUB/c/OSR_CUSTOM_MENU.OSR_ROOM_MATRIX.GBL?PortalActualURL=https%3a%2f%2fcourses.osu.edu%2fpsc%2fcsosuct%2fEMPLOYEE%2fPUB%2fc%2fOSR_CUSTOM_MENU.OSR_ROOM_MATRIX.GBL&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fcourses.osu.edu%2fpsp%2fcsosuct%2f&PortalURI=https%3a%2f%2fcourses.osu.edu%2fpsc%2fcsosuct%2f&PortalHostNode=CAMP&NoCrumbs=yes&PortalKeyStruct=yes"

# Create Driver object with browser driver.
driver = create_driver(DRIVER_PATH)

# Open website.
open_website(driver, ROOM_MATRIX_LINK)

# Load all facilities to search.
facility_id_list = get_facility_ids()

# Create SQLLite database.
conn = sqlite3.connect('classes.db')
c = conn.cursor()

c.execute("""CREATE TABLE classes (
                facility_id text,
                facility_name text,
                day text,
                class_number text,
                start_hour text,
                start_min text,
                end_hour text,
                end_time text
                )""")

for facility_id in facility_id_list:
    # Find room search bar and enter room number.
    search_classroom(driver, facility_id)

    time.sleep(2)

    # Refresh schedule.
    refresh_schedule(driver)

    time.sleep(4)

    # Grabs each individual time box.
    time_boxes = grab_box_info(driver, By.CLASS_NAME, "PSLEVEL3GRIDODDROW")

    # Creates a list of dictionaries, whose entries contain class information.
    weekly_schedule = parse_box_data(time_boxes)

    # Save schedule to SQLite database.
    output_info(c, facility_id, weekly_schedule)

# Close website.
driver.quit()

# Close database connection.
conn.close()
