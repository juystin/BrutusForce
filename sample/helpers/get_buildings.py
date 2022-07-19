import re
import time
import requests
import os

from selenium.webdriver.common.by import By

from sample.helpers.connectors import create_connection
from sample.helpers.connectors import create_driver
from sample.helpers.connectors import load_building_numbers

from dotenv import load_dotenv


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json?"
BUILDING_INDEX_QUERY = "https://www.osu.edu/map/building.php?building="


def format_as_facility_id(string):
    separated_string = re.split('(\d+)', string)
    return separated_string[0] + separated_string[1].rjust(4, "0")


def init_tables(conn):
    cursor = conn.cursor()

    cursor.execute('''DROP TABLE if EXISTS buildings''')
    cursor.execute('''CREATE TABLE buildings
    (building_num text, building_name text, building_abbriev text, address text, link text, lat text, lng text)
    ''')

    cursor.execute('''DROP TABLE if EXISTS classrooms''')
    cursor.execute('''
    CREATE TABLE classrooms
    (building_num text, facility_id text, classroom_name text, link text)
    ''')

    cursor.close()


def open_website(driver, link):
    driver.get(link)


def sort_by_building_numbers(driver):
    sort_by_num_button = driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/"
                                                       "div[1]/div[1]/div[1]/"
                                                       "div[1]/div[1]/div[1]/"
                                                       "form[1]/span[4]")
    enter_button = driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/"
                                                 "div[1]/div[1]/div[1]/"
                                                 "div[1]/div[1]/div[1]/"
                                                 "form[1]/input[1]")
    sort_by_num_button.click()
    enter_button.click()


def geocode_address(address):
    return requests.get(GOOGLE_BASE_URL,
                       params={
                           'key': GOOGLE_API_KEY,
                            'address': address}
                       ).json()['results'][0]['geometry']['location']

def grab_building_info(driver, query, conn, building_numbers):
    cursor = conn.cursor()
    for num in building_numbers:
        driver.get(query + num)
        classrooms = driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/"
                                                   "div[1]/div[1]/div[1]/"
                                                   "div[4]/div[1]/div[3]/"
                                                   "ul[1]").find_elements(By.XPATH, "li")

        building_info = driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/"
                                                      "div[1]/div[1]/div[1]/"
                                                      "div[2]/p[1]").text.splitlines()
        building_name = ' '.join(building_info[0].split()[0:-1])
        building_abbriev = building_info[0].split()[-1]
        address = ', '.join(building_info[2:4])

        geo_coordinates = geocode_address(address)

        cursor.execute(
            '''INSERT INTO buildings (building_num, building_name, building_abbriev, address, link, lat, lng) 
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (num, building_name, building_abbriev, address, query + num, geo_coordinates['lat'], geo_coordinates['lng']))

        for classroom in classrooms:
            cursor.execute(
                '''INSERT INTO classrooms (building_num, facility_id, classroom_name, link) 
                VALUES (?, ?, ?, ?)''',
                (num, format_as_facility_id(building_abbriev + classroom.text.split()[-1]), classroom.text,
                    classroom.get_attribute('href')))

        time.sleep(1.5)
        conn.commit()

    cursor.close()


def populate_building_tables():
    conn = create_connection()

    init_tables(conn)

    driver = create_driver()

    building_numbers = load_building_numbers()

    grab_building_info(driver, BUILDING_INDEX_QUERY, conn, building_numbers)

    driver.close()

    conn.close()


