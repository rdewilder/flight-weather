import pickle, ConfigParser, shutil, os.path
from datetime import timedelta, datetime
from accuweatherday import *
from persistday import *


#  data is a dictionary where the keys are the 4 letter waypoint identifer
#  The values are list of forecast tuples

def generate_dates(end):
    day = timedelta(days=1)
    cur_date = datetime.now().date()
    prev_month = cur_date.month
    dates = []
    while (cur_date <= end_date):
        dates.append(cur_date)
        prev_month = cur_date.month
        cur_date = cur_date + day
    return dates

def refresh_data(dates, waypoints):
    print "refresh_data ..."
    ac = accuweatherday(aw_params)
    cache_dir = time.strftime("%m-%d-%Y")
    print "refreshing data for %s" % cache_dir
    row_format = '"%s","%s",%s,%s,%s,%s,%s,%s,%s,%s,%s\n'
    data = {'waypoints' : waypoints, 'dates' : dates}

    for date in dates:
        row = []
        for waypoint in waypoints:
            cache = "%s/%s-%s.pik" % (cache_dir, waypoint, ac.day)
            forecast = ac.getforcast(waypoint, date)
            row.append(forecast)
            #csv_file.write(row_format % forecast)
            f = open(cache, "w")
            pickle.dump(forecast, f)
            f.close()
        ac.incrementDay()

        data[date] = row
    return data

def load_data(dates, waypoints):
    print "load_data ..."
    cache_dir = time.strftime("%m-%d-%Y")
    data = {'waypoints' : waypoints, 'dates' : dates}
    day = 1
    for date in dates:
        row = []
        for waypoint in waypoints:
            cache = "%s/%s-%s.pik" % (cache_dir, waypoint, day)
            f = open(cache, "r")
            row.append(pickle.load(f))
            f.close()

        day += 1
        data[date] = row

    return data


def get_data(dates, waypoints):
    cache_dir = time.strftime("%m-%d-%Y")
    if not os.path.isdir(cache_dir):
        use_cache = False
        os.makedirs(cache_dir)
        data = refresh_data(dates, waypoints)
    else:
        data = load_data(dates, waypoints)

    return data

## start program logic

config = ConfigParser.RawConfigParser()
config.read('flight-weather.cfg')
env = config.get('App', 'env')
dir = time.strftime("%m-%d-%Y")
isProd = False

if env == 'prod':
    isProd = True
    if os.path.exists(dir):
        shutil.rmtree(dir)

end_date = datetime.strptime(end_date_str, "%d %b %Y").date()
dates = generate_dates(end_date)
data = get_data(dates, waypoints)

r = persistday()
r.save(data, isProd)

sendEmail("Flight Weather Daily Update Success", "The Daily update is complete")
print "Complete"
