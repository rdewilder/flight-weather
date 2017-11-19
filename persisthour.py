import time
import boto3
import sys
from BeautifulSoup import BeautifulSoup as bs
from constants import *
from datetime import datetime, timedelta



class persisthour:

    html_file = "web/forecast-hourly-%s.html"
    remote_file = "forecast-hourly-%s.html"

    modal_template = """
   <div class="modal" id="%s" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
     <div class="modal-dialog" role="document">
       <div class="modal-content">
         <div class="modal-header">
           <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
           <h4 class="modal-title" id="myModalLabel">%s</h4>
         </div>
         <div class="modal-body">
           %s
         </div>
         <div class="modal-footer">
           <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
         </div>
       </div>
     </div>
   </div>
    """

    def generate_modal(self, data, hour):

        label = "%s - %s" % (data['waypoint'], hour)
        text = """
        Condtion: %s <br/>
        Wind: %s <br/>
        Gusts: %s <br/>
        Liquid: %s <br/>
        Ceiling: %s <br/>
        Visibility: %s <br/>
        Waypoint: %s <br/>
        """

        text = text % (data['condition'], data['wind'], data['gusts'],
                       data['liquid'], data['ceiling'], data['visibility'],
                       data['waypoint'])


        return self.modal_template % (data['id'], label, text)

    def save(self, data, isProd = False):
        days = data.keys()
        date = cur_date = datetime.now().date()

        for day in days:
            fileName = self.html_file % day
            remoteName = self.remote_file % day
            html = self.create_html(data[day], date)
            html = bs(html).prettify()
            file = open(fileName, "w")
            file.write(html)
            file.close()
            if isProd:
                self.publish(fileName, remoteName)
            print "%s saved" % fileName
            date = cur_date + timedelta(days=day)

    def publish(self, fileName, remoteName):
        s3 = boto3.client('s3')

        s3.upload_file(fileName, "flight-planner", remoteName,
            ExtraArgs={"ACL": "public-read", "ContentType": "text/html"})

    def create_html(self, day, date):
        template = """
        <html>
        <head>
          <link rel="stylesheet" type="text/css" href="bootstrap.css" />
          <link rel="stylesheet" type="text/css" href="style.css" />
          <style>
           body {
                        font-family: "Lucida Grande", Helvetica, Verdana, sans-serif;
                        font-size: 10pt;
                        line-height: 14pt;
                    }
          </style>
          <script src="https://code.jquery.com/jquery-1.9.1.js"></script>
          <script src="bootstrap.js"></script>
          <script type="text/javascript" src="jquery.freezeheader-new.js"></script>
          <script type="text/javascript">
           $(document).ready(function(){
                        $("#table1").freezeHeader();
                    });
          </script>
          <title>Flight Weather KADS to CA51</title>
        </head>
        <body>
        <div class="container-fluid">

   <!-- Table -->
            %s
    <!-- Modals -->
            %s

    </div>
        </body>
        </html>"""

        t = self.create_table(day, date)
        return template % t

    # Dictionary of days
    #    list of waypoints
    #       Dictionary of hours_precipitation
    #            Dictionary of attributes

    def create_table(self, day, date):
        modal = ""
        dt = time.strftime("%b %d, %Y %I:%M %p %Z")
        table = '<table class="gridView" id="table1"><thead>'
        table += '<tr><th colspan="%s"><span style="font-size:30px">Hourly forecast for %s</span><br>Updated: %s</th></tr>' % \
                 (len(waypoints)+1, date.strftime("%b %d, %Y"), dt)
        table += '<tr><th>Hour</th>'
        for idx, waypoint in enumerate(waypoints):
            table += "<th>%s</th>" % waypoint
        table += "</tr></thead><tbody>"


        for h in day.keys():
            hour = day[h]
            _h = datetime.strptime(str(h), "%H")
            _h = _h.strftime("%I:%M %p")
            table += "<tr>"
            table += '<td>%s</td>' % _h

            for waypoint in waypoints:
                try:
                    fc = hour[waypoint]
                    value = '<a tabindex="0" role="button" data-toggle="modal" data-target="#%s">Summary</a>' % (fc['id'])
                    value += '<br/><a href="%s">Details</a>' % (fc['url'])

                    table += '<td bgcolor="%s">%s</td>' % (self.get_color_code(fc), value)
                    modal += self.generate_modal(fc, _h)
                except KeyError:
                    table += '<td><a tabindex="0" role="button" data-toggle="modal" data-target="#">No Data</a></td>'

            table += "</tr>"
        table += "</tbody></table>"
        return (table, modal)

    def get_color_code(self, data):
        ceiling = int(data['ceiling'].split()[0])
        wind = int(data['wind'].split()[0])
        gusts = int(data['gusts'].split()[0])
        liquid = float(data['liquid'].split()[0])

        color = '548235'

        if ceiling < 20000:
            color = 'A9D08E'
        if wind > 15:
            color = 'A9D08E'

        if ceiling < 15000:
            color = 'E2EFDA'
        if liquid > 0:
            color = 'E2EFDA'

        if ceiling < 10000:
            color = 'F4B084'
        if liquid > 0.1:
            color = 'F4B084'
        if gusts > 20:
            color = 'F4B084'

        if ceiling < 5000:
            color = 'FF0000'
        if wind > 20:
            color = 'FF0000'
        if liquid > 0.2:
            color = 'FF0000'
        if gusts > 30:
            color = 'FF0000'








        return color
