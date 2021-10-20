from io import StringIO, BytesIO
import csv
import zipfile
import pymysql
from datetime import datetime,timedelta


def create_csv(title, results, col_names):
    csv_file = StringIO()
    writer = csv.DictWriter(csv_file, fieldnames=col_names)
    writer.writeheader()
    writer.writerows(results)
    return zip_content(title + ".csv", csv_file.getvalue())


def zip_content(file_name, content):
    zipped_file = BytesIO()
    with zipfile.ZipFile(zipped_file, 'w', zipfile.ZIP_DEFLATED) as zip:
        zip.writestr(file_name, content)
    return zipped_file


def connect_to_db(env='staging'):
    if env == "local":

        endpoint = 'localhost'
        username = 'mani'
        password = 'mani1234@'
        database_name = 'mysql'
    elif env == "staging":
        endpoint = 'cheetay-clone.cwyg8vc3e60v.eu-central-1.rds.amazonaws.com'
        username = 'root'
        password = 'arbisoft313'
        database_name = 'logistics'
    elif env == "preprod":
        endpoint = 'pre-prod-6jan2021.cwyg8vc3e60v.eu-central-1.rds.amazonaws.com'
        username = 'root'
        password = 'ohTha8Eey4eiRohs'
        database_name = 'logistics'
    else:  # production db
        endpoint = 'cheetay-production-rds-read-replica.cwyg8vc3e60v.eu-central-1.rds.amazonaws.com'
        username = 'readonly'
        password = 'wiphu9NijeePuoni'
        database_name = 'logistics'

    connection = pymysql.connect(host=endpoint, port=3306, user=username, passwd=password, db=database_name)
    return connection

def get_dates(start_date, end_date):
        """
        Validate and convert start_date and end_date into start_time and end_time
        """
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        start_time = datetime.strptime('{date} 23:59:00'.format(
            date=start_date - timedelta(days=1)), '%Y-%m-%d %H:%M:%S')
        print(start_time)
        end_time = min(datetime.strptime('{date} 23:59:00'.format(date=end_date),
                                         '%Y-%m-%d %H:%M:%S'), datetime.now())
        result = {'start_time': start_time, 'end_time': end_time, 'start_date': start_date, 'end_date': end_date}
        return result