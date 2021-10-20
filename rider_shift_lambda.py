from utils import *
from sql import *

NAME = 'Name'
CITY = 'City'
NIC = 'CNIC'
ID = 'ID'
MOBILE_NUMBER = 'Mobile Number'
ON_TIME_RATE = 'On Time Rate'


def on_time_report(start_date, end_date):

    data = get_dates( start_date,  end_date)
    start_time, end_time = data['start_time'], data['end_time']
    start_date, end_date = data['start_date'], data['end_date']
    riders_data = []
    riders = get_data(start_time, end_time)
    print('rider', riders[0][0])
    for rider in riders:

        order_stats = get_rider_order_stats(rider[0], start_time, end_time)
        total_picked_up_orders = order_stats['total_picked_up_orders']
        total_delivered_orders = order_stats['total_delivered_orders']
        print('pick',total_picked_up_orders)
        print('del', total_delivered_orders)
        on_time_rates = calculate_on_time_rates(rider[0], start_time, end_time, total_delivered_orders,
                                               total_picked_up_orders)
        on_time_rate = on_time_rates['on_time_rate']

        riders_data.append(
            {ID: rider[0], NAME: rider[1], NIC: rider[2], MOBILE_NUMBER: rider[3], CITY: rider[4],
             ON_TIME_RATE: on_time_rate})

    cumulative_stats = {ID: '', NAME: '', NIC: '', MOBILE_NUMBER: '', CITY: '',
                            ON_TIME_RATE: sum(rider_data[ON_TIME_RATE] for rider_data in riders_data)}
    riders_data.append(cumulative_stats)
    header = [ID, NAME, NIC, MOBILE_NUMBER, CITY, ON_TIME_RATE]
    file_name = 'Rider On Time Report.csv'
    zip_file = create_csv(file_name, riders_data, header)
    attachments = [{'name': file_name + '.zip', 'content': zip_file.getvalue()}]
    title = 'Rider Salary Report  -  {} - {}'.format(start_date, end_date)
    import csv


    with open('countriesasdf.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write the data
        writer.writerow(riders_data)


on_time_report("2021-05-10", "2021-10-10")




