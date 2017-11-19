import time
import boto3
from BeautifulSoup import BeautifulSoup as bs
from constants import *



class persistday:

    html_file = "web/forecast.html"

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

    def generate_modal(self, data):
        label = "%s - %s" % (data['waypoint'], data['date'].strftime("%b %d"))
        text = """
        <img src="%s"></img><br/>
        <b>%s</b><p/><br/>
        Wind: %s<br/>
        Gusts: %s<br/>
        Rain: %s<br/>
        T-storms: %s<br/>
        Snow: %s<br/>
        Ice: %s<br/>
        """
        text = text % (data['image'], data['description'], data['wind'],
                       data['gusts'], data['rain'], data['tstorms'], data['snow'],
                       data['ice'])
        return self.modal_template % (data['id'], label, text)

    def save(self, data, isProd = False):
        html = self.create_html(data)
        soup=bs(html)
        html = prettyHTML=soup.prettify()
        file = open(self.html_file, "w")
        file.write(html)
        file.close()
        if isProd:
            self.publish()
        print "saved"

    def publish(self):
        s3 = boto3.client('s3')

        s3.upload_file(self.html_file, "flight-planner", "forecast.html",
            ExtraArgs={"ACL": "public-read", "ContentType": "text/html"})

    def create_html(self, data):
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
            jQuery(document).ready(function($) {
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

        t = self.create_table(data)
        return template % t

    def create_table(self, data):
        dates = data['dates']
        waypoints = data['waypoints']
        date = datetime.now().date()

        modal = ""
        dt = time.strftime("%b %d, %Y %I:%M %p %Z")
        table = '<table class="gridView" id="table1"><thead>'
        table += '<tr><th colspan="%s"><span style="font-size:30px">Daily Forecast</span><br>Updated: %s</th></tr>' % \
                 (len(waypoints)+1, dt)
        table += '<tr><th>Date</th>'
        for idx, waypoint in enumerate(waypoints):
            table += "<th>%s</th>" % waypoint
        table += "</tr></thead><tbody>"

        hourly_page = 'forecast-hourly-%s.html'

        for idx, date in enumerate(dates, 1):
            fc_list = data[date]
            table += "<tr>"
            if idx < 16:
                table += '<td>%s<br/><a href="%s">Hourly</a></td>' % (date.strftime("%b %d"), hourly_page % idx)
            else:
                table += '<td>%s</td>' % (date.strftime("%b %d"))
            for fc in fc_list:
                value = '<a tabindex="0" role="button" data-toggle="modal" data-target="#%s">Summary</a>' % fc['id']
                value += '<br><a href="%s">Details</a>'
                value = value % (fc['url'])
                table += '<td bgcolor="%s">%s</td>' % (self.get_color_code(fc), value)
                modal += self.generate_modal(fc)
            table += "</tr>"

        table += "</tbody></table>"
        dt = time.strftime("%b %d, %Y %I:%M:%S %p %Z")
        return (table, modal)

    def get_color_code(self, data):
        color = None
        x = data['image'].split('/').pop().split('.')
        x = int(x[0])

        if x == 1:
            color = '548235'
        elif x == 2:
            color = 'A9D08E'
        elif x == 3:
             color = 'E2EFDA'
        elif x == 4:
            color = 'FCE4D6'
        elif x == 6:
             color = 'FCE4D6'
        elif x == 7:
             color = 'F4B084'
        elif x > 7:
            color = 'FF0000'
        else:
            print x

        return color
