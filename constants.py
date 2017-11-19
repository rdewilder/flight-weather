import Mail
from datetime import datetime

def sendEmail(subject, message):
    mail = Mail.Mail("robert.dewilder@gmail.com", subject)
    mail.text(message)
    mail.send()

waypoints = ['KADS','KHOB','KELP','KDMN','KTUS','Gila Bend',
             'KBLH','KAPV','KPMD','KMAE','KPRB','CA51']


start_hour = datetime.strptime('7am', '%I%p').hour
end_hour = datetime.strptime('8pm', '%I%p').hour

aw_params = dict([('KADS', ('addison-airport-tx', '8499_poi', '75001')), \
                  ('KHOB', ('lea-county-regional-airport-nm', '7895_poi', '88231')), \
                  ('KELP', ('el-paso-international-airport-tx', '8396_poi', '79901')), \
                  ('KDMN', ('deming-municipal-airport-nm', '7425_poi', '88030')), \
                  ('KTUS', ('tucson-international-airport-az', '9018_poi', '85716')), \
                  ('Gila Bend', ('gila-bend-az', '331842', '85337')), \
                  ('KBLH', ('blythe-airport-ca', '6852_poi', '92225')), \
                  ('KAPV', ('apple-valley-airport-ca', '8326_poi', '92307')), \
                  ('KPMD', ('palmdale-regional-usaf-plant-42-airport-ca', '10042_poi', '93550')), \
                  ('KMAE', ('madera-municipal-airport-ca', '8820_poi', '93637')), \
                  ('KPRB', ('paso-robles-municipal-airport-ca', '9190_poi', '93446')), \
                  # The sea ranch / airstrip data not available
                  ('CA51', ('sea-ranch-ca', '2179249', '95412'))
                ])

fc_colors = dict([('perfect', '#548235'), ('good', 4127), ('fair', 4098),('maginal', 4098),('bad', 4098)])

date_xpath = 'string (//*[@id="two-day"]/div[@class="hider"]/ul/h3/text())'

desc_xpath = 'string(//*[@id="two-day"]/div[@class="hider"]/ul/li[1]/dl/dd[3]/p/text())'
wind_xpath = 'string(//*[@id="details"]/div[1]/div/div[1]/p/span/text()[2])'
gusts_xpath = 'string(//*[@id="details"]/div[1]/div/div[1]/p/span/text()[4])'
rain_xpath = 'string(//*[@id="details"]/div[1]/div/div[2]/p[1]/text())'
tstorm_xpath = 'string(//*[@id="details"]/div[1]/div/div[2]/p[2]/text())'
snow_xpath = 'string(//*[@id="details"]/div[1]/div/div[2]/p[3]/text())'
ice_xpath = 'string(//*[@id="details"]/div[1]/div/div[2]/p[4]/text())'

end_date_str = "25 Nov 2017"

