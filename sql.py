from utils import *


def get_data(start_time, end_time):
    get_data_query = ("""SELECT r.id,CONCAT(au.first_name ,' ',au.last_name) ridername,r.nic ,r.mobile_number,c.name FROM rider r  
                        LEFT OUTER JOIN city c ON (r.city_id = c.id) INNER join auth_user au on au.id = r.user_id 
                        WHERE 
                        r.id IN (SELECT rs.rider_id FROM rider_shift rs INNER JOIN shift s ON 
                        (rs.shift_id = s.id) WHERE s.start_at BETWEEN '{}' AND '{}') 
                        
""".format(start_time, end_time))
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(get_data_query)

    shifts = cursor.fetchall()
    return shifts


def get_rider_order_stats(rider, start_time, end_time):
    get_rider_order_stats_query = ("""select COUNT(o.id) as total_orders,
                                 COUNT(case when os.picked_up_at IS not NULL then os.id end) as total_picked_up_orders ,
                                 COUNT(case when os.delivered_at IS NOT NULL  then os.id end) as delivered_orders
                                      
                                    from order_state os 
                                    inner join `order` o on os.order_id = o.id 
                                    
                                    WHERE (os.assigned_at BETWEEN '{}' AND '{}'
                                    AND o.status in ("Delivered", "Cancelled", "Failed", "Invalid") 
                                    AND os.rider_id='{}')  """.format(start_time, end_time, rider))
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(get_rider_order_stats_query)

    shifts = cursor.fetchall()
    total_orders = shifts[0][0] or 0
    total_picked_up_orders = shifts[0][1] or 0
    delivered_orders = shifts[0][2] or 0
    total_failed_orders = total_picked_up_orders - delivered_orders
    return {
        'total_orders': total_orders,
        'total_picked_up_orders': total_picked_up_orders,
        'total_delivered_orders': delivered_orders,
        'total_failed_orders': total_failed_orders,
        'failed_rate': (round(total_failed_orders * 100 / total_picked_up_orders, 1)
                        if total_picked_up_orders else 0),
    }


def calculate_on_time_rates(rider, start_time, end_time,total_delivered_orders, total_picked_up_orders):
    on_time_delivery_stats = get_rider_on_time_delivery_stats(rider, start_time, end_time)
    total_on_time_deliveries = on_time_delivery_stats['total_on_time_deliveries']
    on_time_pickup_stats = get_rider_on_time_pickup_stats(rider, start_time, end_time)
    total_on_time_pickups = on_time_pickup_stats['total_on_time_pickups']

    return {"drop_off_rate": round(total_on_time_deliveries * 100 / (total_delivered_orders or 1)),
            "pickup_rate": round(total_on_time_pickups * 100 / (total_picked_up_orders or 1)),
            "on_time_rate": get_on_time_rate(total_on_time_deliveries, total_on_time_pickups, total_delivered_orders,
                                             total_picked_up_orders)}


def get_rider_on_time_delivery_stats(rider, start_time, end_time):
    get_rider_on_time_delivery_stats_sql = ("""select COUNT(o.id)  from order_state os inner join `order` o ON os.order_id = o.id 
                                            inner join algo_order_times aot on o.id =aot.order_id 
                                            WHERE (os.arrived_for_delivery_at <= (CASE WHEN aot.delivery_time_after_pickup IS NOT NULL THEN 
                                            aot.delivery_time_after_pickup 
                                            WHEN aot.delivery_time_after_pickup IS NULL THEN aot.delivery_time ELSE NULL END) AND 
                                            os.assigned_at BETWEEN '{}' AND '{}' AND os.delivered_at IS NOT NULL AND o.status = "Delivered" AND 
                                            os.rider_id = '{}')""".format(start_time, end_time, rider))

    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(get_rider_on_time_delivery_stats_sql)
    get_rider_on_time = cursor.fetchall()
    return {
        'total_on_time_deliveries': get_rider_on_time[0][0]
    }


def get_rider_on_time_pickup_stats(rider, start_time, end_time):

    get_rider_on_time_pickup_stats_sql = ("""select COUNT(o.id)  from order_state os inner join `order` o ON os.order_id = o.id 
                                            inner join algo_order_times aot on o.id =aot.order_id 
                                            WHERE  (os.arrived_at <= (aot.rider_arrival_time) AND 
                                            os.assigned_at BETWEEN '{}' AND '{}' AND o.status IN 
                                            ("Delivered", "Cancelled", "Failed", "Invalid") AND os.picked_up_at IS NOT NULL AND os.rider_id = '{}')
                                            """.format(start_time, end_time, rider))

    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(get_rider_on_time_pickup_stats_sql)
    get_rider_on_time_pickup = cursor.fetchall()
    return {
        'total_on_time_pickups': get_rider_on_time_pickup[0][0]
    }


def get_on_time_rate(on_time_deliveries, on_time_pickups, total_delivered_orders, total_picked_up_orders):
    return int(round((on_time_deliveries + on_time_pickups) * 100 /
                     ((total_delivered_orders + total_picked_up_orders) or 1), 0))
