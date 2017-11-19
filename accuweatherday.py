import requests, time, sys
import constants, secrets
import re
from lxml import html
from datetime import datetime

class accuweatherday:

    daily_url = secrets.daily_url
    calibrate_url = secrets.daily_calibrate_url
    date_xpath = constants.date_xpath

    day = 1

    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
        }
    )

    def __init__(self, params):
        errors = self.validateDates(params)
        text = ''
        if len(errors) > 0:
            for error in errors:
                text += "%s\n" % error
            print "Aborting update ... dates are not in sync"
            constants.sendEmail("Flight Weather Daily Date Sync Error", text)
            sys.exit()

        print "Dates are in sync"

    def validateDates(self, params):
        cur_date = datetime.now().date()
        cur_month = time.strftime("%B").lower()
        cur_day = int(cur_date.day)

        results = []
        for key, value in params.iteritems():
            url = self.calibrate_url % (value[0], value[2], value[1])
            r = requests.get(url, headers=self.headers)
            tree = html.fromstring(r.content)
            date = tree.xpath(self.date_xpath).split()
            ac_month = date[0].lower()
            ac_day = int(date[1])

            print "validting waypoint %s\n" % key
            if not (cur_month == ac_month and cur_day == ac_day):
                print "Waypoint %s not is sync" % key
                results.append(key)
        return results


    def incrementDay(self):
        self.day += 1

    def getforcast(self, waypoint, date):
        data = {}
        param = constants.aw_params[waypoint]
        url = self.daily_url % (param[0], param[2], param[1], self.day)
        r = requests.get(url, headers=self.headers)
        tree = html.fromstring(r.content)
        data['id'] = "%s-%s" % (waypoint.replace(" ", ""), self.day)
        data['description'] = str(tree.xpath(constants.desc_xpath)).strip()
        data['wind'] = str(tree.xpath(constants.wind_xpath)).strip()
        data['gusts'] = str(tree.xpath(constants.gusts_xpath)).strip()
        data['rain'] = str(tree.xpath(constants.rain_xpath)).strip()
        data['tstorms'] = str(tree.xpath(constants.tstorm_xpath)).strip()
        data['snow'] = str(tree.xpath(constants.snow_xpath)).strip()
        data['ice'] = str(tree.xpath(constants.ice_xpath)).strip()
        data['waypoint'] = waypoint
        data['url'] = url
        data['date'] = date

        m = re.search('(https://vortex.accuweather.com/adc2010/m/images/icons/600x212/slate/\d\d.png)', r.content)
        data['image'] = m.group(0)

        return data
