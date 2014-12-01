""" 
@note: Maccabee, I made some small changes to this script from your original. 
       Adapted it to work with plone context.
"""

import base64
import gdata.calendar.service
import datetime
import time as _time
# credit: http://home.blarg.net/~steveha/pyfeed.html
from feed.date import rfc3339 

class HoursLookup:

    
    def __init__(self,context):
        self.context = context
        self.service = gdata.calendar.service.CalendarService()
        self.service.email = self.getProperty("google_username")
        self.service.password = base64.decodestring(self.getProperty("google_password_base64"))
        self.service.source = self.getProperty("google_service_source")
        self.service.ProgrammaticLogin()
        
        
    def getProperty(self,prop_name):
        return self.context.portal_properties.groupfinder_properties.getProperty(prop_name,"");
        
    def getMainHoursForToday(self):
        today = datetime.datetime.now()
        return self.getMainHoursForDate(today)
            
    def getMainHoursForDate(self, date):
        MAIN_CALENDAR = self.getProperty("google_main_calendar")
        permission = self.getProperty("google_visibility")
        access = self.getProperty("google_visibility_access")
        query = gdata.calendar.service.CalendarEventQuery(MAIN_CALENDAR,permission,access)
        
        # we want the first hours after 2am today, so normalize time
        date = date.replace(hour=2, minute=0, second=0, microsecond=0)
        
        query.start_min = to_rfc3339(date)
        query.start_max = to_rfc3339(date + datetime.timedelta(days=1))
        
        #Attempt Connection
        try:
            feed = self.service.CalendarQuery(query)
        except Exception as e:
            return Hours(False, closed_date=date)
        
        #print ""
        #print "FEED WHEN:" + str(feed.entry[0].when[0])
        #print ""
        
        #print ""
        #print "FEED ENTRY:" + str(feed.entry[0].event_status.value)
        #print ""
        
        if len(feed.entry) == 0 or str(feed.entry[0].event_status.value) == "CANCELED":
            #print 'closed'
            return Hours(False, closed_date=date)
            
            
        #print 'open'
        # assume only one event today, with one 'when' period
        event = feed.entry[0]
        when = event.when[0]
        #print 'event:', event
        #print 'when:', when
        #return Hours(when.start_time, when.end_time)
        #print "HOURS: " + str(Hours(True, when=when))
        return Hours(True, when=when)

    def isLibraryClosed(data):
        pass
        

class Hours:
    DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

    def __init__(self, is_open, when=None, closed_date=None):
        self.is_open = is_open
        if when != None:
            if self.is_open:
                self.start = self._parse_when(when.start_time)
                self.end = self._parse_when(when.end_time)
            else:
                self.start = closed_date

    def _parse_when(self, rfc_time):
        dt = from_rfc3339(rfc_time)
        return dt
        
    def format_day(self):
        return Hours.DAYS[self.start.weekday()]
    
    def format_casual(self):
        return "%s - %s" % (self._format_time_casual(self.start), 
            self._format_time_casual(self.end))

    def _format_time_casual(self, time):
        return time.strftime('%1I:%M%p').lower().lstrip('0').replace(
':00', '')
            
    def __str__(self):
        return'Hours (start: %s, end: %s)' % (self.start, self.end,)
        

class HoursWriter:
    HTML_PREFIX = '<span class="tinytext" name="">'
    HTML_SUFFIX = '</span>'

    def write(self, hours, filename):
        output_text = self.format(hours)
        self.write_to_file(output_text, filename)

    def format(self, hours):
        text = hours.format_day()
        if not hours.is_open:
            text += ': Closed'
        else:
            text += ': ' + hours.format_casual()
        text = HoursWriter.HTML_PREFIX + text + HoursWriter.HTML_SUFFIX
        #print 'returning text:', text
        return text
        
    def write_to_file(self, output_text, filename):
        try:
            f = open(filename, 'w')
            f.write(output_text + '\n')
            print 'Wrote to file:', filename
        except IOError:
            print 'Error writing to file:', filename
        try :
            f.close()
        except:
            print 'could not close file handle'
    
def to_rfc3339(dt):
    tf = _time.mktime(dt.timetuple())
    return rfc3339.timestamp_from_tf(tf)

def from_rfc3339(rfc_time):
    tf = rfc3339.tf_from_timestamp(rfc_time)
    return datetime.datetime.fromtimestamp(tf)
    
#lookup = HoursLookup()
#today_hours = lookup.getMainHoursForToday()
#writer = HoursWriter()
#writer.write(today_hours, '../scripts/today_main_hours.txt')
