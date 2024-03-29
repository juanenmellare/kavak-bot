import json
import smtplib
import sys
import time
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import schedule
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = 'www.kavak.com'
https_base_url = 'https://' + base_url
api_advanced_search = https_base_url + '/api/advanced-search-api/v2/advanced-search?loan_limit=true'
cars_sent_txt_path = 'cars_sent.txt'


def get_current_time_for_log():
    now = datetime.now()
    return now.strftime('\033[0;0m%H:%M:%S | ')


def base_log(color, message):
    print(get_current_time_for_log() + color + message)


def log(message):
    base_log('', message)


def get_config():
    with open('config.json') as json_file:
        return json.load(json_file)


def build_session():
    country_acronym = config['country_acronym']

    session = requests.Session()
    session.verify = False
    session.trust_env = False
    headers = {
        'authority': base_url,
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'es-419,es;q=0.9,en;q=0.8',
        'kavak-client-type': 'web',
        'kavak-country-acronym': country_acronym,
        'referer': f'{https_base_url}/{country_acronym}/usados'
    }
    session.headers = headers

    return session


def format_query_parameter(filter_value):
    return ','.join([str(value) for value in filter_value if value]) if type(filter_value) is list else str(
        filter_value)


def build_query_parameters():
    filters = config['filters']

    query_parameters = ''
    for filter_key in filters:
        filter_value = filters[filter_key]
        filter_value_formatted = format_query_parameter(filter_value)
        if filter_key[0] != '_':
            query_parameters = f'{query_parameters}&{filter_key}={filter_value_formatted}'

    return query_parameters


def get_filtered_cars(query_parameters):
    session = build_session()
    api_advanced_search_with_filters = api_advanced_search + query_parameters + '&page='

    page = 0
    total_pages = 1
    cars = []
    while page < total_pages:
        time.sleep(1)
        advanced_search_url = api_advanced_search_with_filters + str(page)
        advanced_search_result = session.get(url=advanced_search_url)
        advanced_search_result_json = advanced_search_result.json()
        total_pages = advanced_search_result_json['pagination']['total']
        cars = cars + advanced_search_result_json['cars']
        page = page + 1

    order = config['filters'].get('order')
    if order:
        has_to_reverse = True if order == 'higher_price' else False
        cars.sort(reverse=has_to_reverse, key=lambda car: int(car['price'].replace('$ ', '').replace('.', '')))

    return cars


def send_email(subject, content):
    smtp = config['smtp']

    user = smtp['user']
    you = config['receiver']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = you
    html_content = MIMEText(content, 'html')
    msg.attach(html_content)
    mail = smtplib.SMTP(smtp['host'], smtp['port'])
    mail.ehlo()
    mail.starttls()
    mail.login(user, smtp['password'])
    mail.sendmail(user, you, msg.as_string())
    mail.quit()


def save_cars_sent(cars):
    cars_ids = map(lambda car: car['id'], cars)
    file = open(cars_sent_txt_path, 'w')
    file.write(','.join(cars_ids))
    file.close()


def read_cars_sent():
    try:
        file = open(cars_sent_txt_path, 'r')
        file_content = file.read()
        return file_content.split(',') if file_content else []
    except FileNotFoundError as _:
        return []


def filter_not_sent_cars(cars, sent_cars_ids):
    return list(filter(lambda car: car['id'] not in sent_cars_ids, cars))


def build_cars_table(cars, table_name):
    table_rows = ''
    for car in cars:
        table_rows = (table_rows +
                      f'<tr>'
                      f'<td><a href="{car["url"]}">{car["name"]}</a></td>'
                      f'<td>{car["price"]}</td>'
                      f'<td>{car["year"]}</td>'
                      f'<td>{car["km"].replace(" km", "")}</td>'
                      f'<td>{car["transmission"]}</td>'
                      f'<td>{car["color"]}</td>'
                      f'</tr>')

    return """\
        <div class="cars-table">
            <p><b>""" + f'{table_name} ({str(len(cars))})' + """</b></p>
            <table>
                <thead>
                    <tr>
                        <th>Car</th>
                        <th>Price</th>
                        <th>Year</th>
                        <th>Km</th>
                        <th>Transmission</th>
                        <th>Color</th>
                    </tr>
                </thead>
                <tbody>""" + table_rows + """</tbody>
            </table>
        </div>
    """


def send_cars_email(not_sent_cars, cars, query_parameters):
    usados_url_href = f'{https_base_url}/{config["country_acronym"]}/usados{query_parameters.replace("&", "?", 1)}'
    not_sent_cars_table = build_cars_table(not_sent_cars, 'Not seen/Recently added')
    cars_table = build_cars_table(cars, 'All')

    subject_car_q = 'car' if len(not_sent_cars) == 1 else 'cars'
    subject = f'KAVAK BOT - {len(not_sent_cars)} {subject_car_q} not seen/recently added'
    cars_content = """\
    <html>
      <head>
        <style>
            a {
                color: #1351ec;
            }
            
            .cars-table {
                overflow: auto;
                width: 100%;
            }

            .cars-table table {
                border: 1px solid #dededf;
                height: 100%;
                width: 100%;
                border-collapse: collapse;
                border-spacing: 1px;
                text-align: left;
            }

            .cars-table caption {
                caption-side: top;
                text-align: left;
            }

            .cars-table th {
                border: 1px solid #e7e9ee;
                background-color: #000000;
                color: #ffffff !important;
                padding: 5px;
            }

            .cars-table td {
                border: 1px solid #e7e9ee;
                background-color: #ffffff;
                color: #000000;
                padding: 5px;
            }
            
            .cars-table td a {
                text-decoration: none;
                color: inherit;
            }
            </style>
      </head>
      <body>
        <a href='""" + usados_url_href + """'>Kavak - Search Link</a>
        """ + not_sent_cars_table + """<br/>
        """ + cars_table + """
      </body>
    </html>
    """

    send_email(subject, cars_content)


def execute_job():
    try:
        log('Looking for cars...')

        query_parameters = build_query_parameters()
        filtered_cars = get_filtered_cars(query_parameters)
        log(f'Cars found: {len(filtered_cars)}...')

        cars_sent = read_cars_sent()
        not_sent_filtered_cars = filter_not_sent_cars(filtered_cars, cars_sent)
        log(f'Not seen/Recently added cars: {len(not_sent_filtered_cars)}...')

        if not_sent_filtered_cars:
            send_cars_email(not_sent_filtered_cars, filtered_cars if cars_sent else [], query_parameters)
            log("Cars email sent...")

            save_cars_sent(filtered_cars)
            log("Cars found saved...")
    except Exception as e:
        log(f'ERROR: {str(e)}')
        traceback.print_exception(*sys.exc_info())


if __name__ == '__main__':
    log('------------ KAVAK BOT -----------')
    config = get_config()

    execute_job()

    search_rate_per_minutes = config['search_rate_per_minutes']
    if search_rate_per_minutes:
        schedule.every(search_rate_per_minutes).minutes.do(execute_job)

        while True:
            schedule.run_pending()
            time.sleep(1)
