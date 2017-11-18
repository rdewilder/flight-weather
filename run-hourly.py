import pickle, ConfigParser, shutil, os.path
from accuweatherhour import *
from persisthour import *
from datetime import datetime, timedelta

#  data is a dictionary where the keys are the 4 letter waypoint identifer
#  The values are list of forecast tuples

cache_dir = time.strftime("%m-%d-%Y-daily")


def refresh_data(waypoints):
    ac = accuweatherhour(aw_params)
    if len(ac.syncErrors) > 0:
        text = ''
        for e in ac.syncErrors:
            text += "%s\n" % e
            sendEmail("Flight Weather Hourly Sync Error", text)
            sys.exit()



    for waypoint in waypoints:
        cur_date = datetime.now().date()
        for day in range(1 + ac.startHours[waypoint][1], 16):
            forecast = ac.getforecast(waypoint, day, cur_date)
            cur_date += timedelta(days=1)
            for key, value in forecast.iteritems():
                cache = "%s/%s-%s-%s.pik" % (cache_dir, waypoint, day, key)
                value['id'] = '%s-%s-%s' % (waypoint.replace(" ", ""), day, key)
                f = open(cache, "w")
                pickle.dump(value, f)
                f.close()  # Dictionary of Days


#    - dictionary of hours
#       - dictionary of waypoints
#          - dictioary of attributes


def load_data(waypoints):
    data = {}
    for d in range(1, 16):
        day = {}
        for h in range(start_hour, end_hour):
            row = {}
            for waypoint in waypoints:
                cache = "%s/%s-%s-%s.pik" % (cache_dir, waypoint, d, h)
                try:
                    f = open(cache, "r")
                    row[waypoint] = pickle.load(f)
                    f.close()
                except IOError:
                    print "Error opening %s" % cache
            day[h] = row
        data[d] = day
    return data


def get_data(waypoints):
    if not os.path.isdir(cache_dir):
        print "Refreshing data"
        use_cache = False
        os.makedirs(cache_dir)
        refresh_data(waypoints)

    print "Loading from cache"
    data = load_data(waypoints)

    return data


## start program logic

config = ConfigParser.RawConfigParser()
config.read('flight-weather.cfg')
env = config.get('App', 'env')
isProd = False

if env == 'prod':
    isProd = True
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

end_date = datetime.strptime("28 Feb 2018", "%d %b %Y").date()

data = get_data(waypoints)
r = persisthour()
r.save(data, isProd)

sendEmail("Flight Weather Hourly Update Success", "The hourly update is complete")

print "Complete"
