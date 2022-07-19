import requests

from sample.helpers.connectors import create_connection


def init_table(conn):
    cursor = conn.cursor()

    cursor.execute('''DROP TABLE if EXISTS classes''')
    cursor.execute('''
    CREATE TABLE classes
    (building_num text, class_title text, class_desc text, units text, class_type text, class_subject text, 
    class_number text, facility_id text, day text, start_time text, end_time text)
    ''')

    cursor.close()


def get_subject_list():
    subject_list = []
    response = requests.get(f"https://content.osu.edu/v2/classes/search?q=&p=&term=1228&campus=col").json()

    # Albeit the Subject filter is known to be in the third index of the filters object array,
    # still perform a search for the Subject filter in case the API changes this in the future.
    for filter_type in response["data"]["filters"]:
        if filter_type["title"] == "Subject":
            for subject in filter_type["items"]:
                subject_list.append(subject["term"])

    return subject_list


def get_building_number(conn, facility_id):
    if facility_id == "ONLINE":
        return "0"
    cursor = conn.cursor()
    cursor.execute('''
        SELECT building_num FROM classrooms WHERE facility_id=?
        ''', [facility_id])
    try:
        building_number = cursor.fetchall()[0]
    except IndexError as e:
        return "-1"
    cursor.close()
    return ''.join(building_number)


def get_building_name(conn, building_number):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT building_name FROM buildings WHERE building_no=?
    ''', [building_number])
    building_name = cursor.fetchall()[0]
    cursor.close()
    return ''.join(building_name)


def get_response_by_subject(subject, page_number):
    return requests.get(f"https://content.osu.edu/v2/classes/search?q=&p=" + str(page_number) + "&term=1228&campus=col&subject=" + subject).json()


def convert_to_24_hr(time):
    if time is None:
        return time

    if (time[1] == ":"):
        time = "0" + time

    if (time[6:] == "pm" and time[0:2] != "12"):
        time = str((int(time[0:2])) + 12) + time[2:]

    return time[0:5]

def run_query_on_subject(conn, subject):
    current_page = 1

    cursor = conn.cursor()

    response = get_response_by_subject(subject, current_page)

    total_pages = response["data"]["totalPages"]

    while current_page <= total_pages:
        response = get_response_by_subject(subject, current_page)
        courses = response["data"]["courses"]

        for course in courses:
            course_info = course["course"]

            try:
                class_title = course_info["title"]
            except KeyError as e:
                class_title = course_info["description"].splitlines()[0]
            class_desc = course_info["description"].splitlines()[0]
            try:
                units = course_info["maxUnits"]
            except KeyError as e:
                units = 0
            try:
                class_type = course_info["component"]
            except KeyError as e:
                class_type = "Other"
            class_subject = course_info["subject"]
            class_number = course_info["catalogNumber"]

            for section in course["sections"]:
                for meeting in section["meetings"]:
                    meeting_days = []
                    facility_id = meeting["facilityId"]

                    if meeting["monday"]: meeting_days.append("Monday")
                    if meeting["tuesday"]: meeting_days.append("Tuesday")
                    if meeting["wednesday"]: meeting_days.append("Wednesday")
                    if meeting["thursday"]: meeting_days.append("Thursday")
                    if meeting["friday"]: meeting_days.append("Friday")

                    start_time = meeting["startTime"]
                    end_time = meeting["endTime"]

                    for day in meeting_days:
                        cursor.execute('''
                        INSERT INTO classes
                        (building_num, class_title, class_desc, units, class_type, class_subject, 
                        class_number, facility_id, day, start_time, end_time) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (get_building_number(conn, facility_id), class_title, class_desc, units, class_type, class_subject,
                              class_number, facility_id, day, convert_to_24_hr(start_time), convert_to_24_hr(end_time)))

        conn.commit()

        current_page = current_page + 1

    cursor.close()


def get_classes(conn):
    subject_list = get_subject_list()

    for subject in subject_list:
        run_query_on_subject(conn, subject)


def populate_classes_table():
    conn = create_connection()
    init_table(conn)
    get_classes(conn)
    conn.close()
