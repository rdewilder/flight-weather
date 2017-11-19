import requests, sys, re
import constants, secrets
from lxml import html
from datetime import *

class accuweatherhour:

    login_url = secrets.hourly_login_url
    hourly_url = secrets.hourly_url
    login_payload = {'username': secrets.username, 'password': secrets.password, 'action': 'Login', \
                    'membershipType': 'premium'}

    calibrate_url = secrets.hourly_calibrate_url

    xpath_date = 'string(//*[@id="fcstContentBox"]/div[1]/text())'
    xpath_start_time = 'string(//*[@id="fcstContentBox"]/div[4]/div[2]/div/div[1]/span/text())'
    # index in div[%s] starts at 2
    xpath_condition = 'string(//*[@id="fcstContentBox"]/div[4]/div[%s]/div/div[3]/img/@alt)'
    xpath_wind = 'string(//*[@id="fcstContentBox"]/div[4]/div[%s]/div/div[9]/text())'
    xpath_gusts = 'string(//*[@id="fcstContentBox"]/div[4]/div[%s]/div/div[10]/text())'
    xpath_liquid = 'string(//*[@id="fcstContentBox"]/div[4]/div[%s]/div/div[18]/text())'
    xpath_ceiling = 'string(//*[@id="fcstContentBox"]/div[4]/div[%s]/div/div[24]/text())'
    xpath_visibility = 'string(//*[@id="fcstContentBox"]/div[4]/div[%s]/div/div[25]/text())'

    session = requests.Session()
    session.post(login_url, data=login_payload, allow_redirects=False)

    syncErrors = []
    # list of first available hour for each waypoint
    startHours = {}

    params = None

    def __init__(self, params):
        self.params = params
        self.syncErrors = self.validateDates()

    def validateDates(self):
        cur_date = datetime.now().date()
        results = []
        for key, value in self.params.iteritems():
            url = self.calibrate_url % (value[1])
            r = self.session.get(url)
            ac_date = self.getDate(r.content)

            if not cur_date == ac_date:
                print "Waypoint %s not is sync" % key
                results.append(key)

            self.startHours[key] = (self.getStartHour(r.content), (cur_date - ac_date).days)
        return results

    def getDate(self, content):
        xpath = 'string(//*[@id="fcstContentBox"]/div[1]/text())'
        tree = html.fromstring(content)
        text =  tree.xpath(xpath).strip()

        m = re.search('(\d+/\d+/\d+)', text)
        if m is None:
            constants.sendEmail("Flight Weather Hourly Null Date Error", "Could not lookup date")
            sys.exit()

        return datetime.strptime(m.group(0), "%m/%d/%Y").date()


    def getStartHour(self, content):
        tree = html.fromstring(content)
        val = tree.xpath(self.xpath_start_time).strip()

        if val == 'Noon':
            return 12

        hour = datetime.strptime(val, '%I%p').hour
        if hour <= constants.start_hour:
            return constants.start_hour
        if hour > constants.end_hour:
            return constants.end_hour
        return hour

    # get days worth of hourly forcast between 8am - 8pm
    # Todo: confirm date in webpage matches expected date
    def getforecast(self, waypoint, day, cur_date):
        data = {}
        loc = constants.aw_params[waypoint]
        start = constants.start_hour

        if day == 1:
            start = self.startHours[waypoint][0]

        j = 0

        for i in range(start, constants.end_hour):
            fc = {}
            if j % 8 == 0:
                url = self.hourly_url % (loc[1], ((day -1)* 24) + (start + j))
                r = self.session.get(url)
                tree = html.fromstring(r.content)
                page_date = self.getDate(r.content)

            k = (j % 8) + 2
            fc['condition'] = tree.xpath(self.xpath_condition % k)
            fc['wind'] = tree.xpath(self.xpath_wind % k)
            fc['gusts'] = tree.xpath(self.xpath_gusts % k)
            fc['liquid'] = tree.xpath(self.xpath_liquid % k)
            fc['ceiling'] = tree.xpath(self.xpath_ceiling % k)
            fc['visibility'] = tree.xpath(self.xpath_visibility % k)
            fc['waypoint'] = waypoint
            fc['url'] = url
            data[i] = fc

            j += 1
        return data
