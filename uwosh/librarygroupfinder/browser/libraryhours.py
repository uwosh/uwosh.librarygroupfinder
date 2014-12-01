# LibraryHours Class
#  - Shows the Library Hours for a particular Date
#  - Formatted for GroupFinder
#
# Notes:
#  - Uses hours_lookup.py class which contacts Google.


from uwosh.librarygroupfinder.browser.hours_lookup import HoursLookup, Hours

from uwosh.librarygroupfinder.browser.validator import Validation

from datetime import datetime as odatetime
import datetime
import time
import simplejson

class LibraryHours:

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    # Controller for Requests
    def __call__(self):
        form = self.request.form
        
        if form.get('option','') == 'all':
            return self.getAllDaysHours(form.get('date',None))
        else:
            try:
                date = form.get('date',False)
                d = date.split("-")
                dt = datetime.datetime(int(d[0]), int(d[1]), int(d[2]),0,0,0)
                libraryHours = HoursLookup(self.context)
                currentHours = libraryHours.getMainHoursForDate(dt)
                
                if currentHours.is_open:
                    return self.doPublicOpenResponse(currentHours)
                else:
                    return self.doClosedResponse(currentHours, d)
            except ValueError:
                response = simplejson.dumps({'Error':'An error occurred'})
                return response
    
    
    def doClosedResponse(self,currentHours,d):
        results = {'opens': 0, 'closes': 0, 'past':1, 'closed':1}
        response = simplejson.dumps(results)
        return response

    def doPublicOpenResponse(self,hours):
        today = odatetime.today()
        if today.hour+2 > hours.end.hour-2 and today.day == hours.end.day and today.month == hours.end.month:
            past = 1
        else:
            past = 0
            
        if hours.start.day != odatetime.today().day or hours.start.month != odatetime.today().month:
            start = hours.start.hour
        else:
            start = odatetime.today().hour + 2
        
        end = self.determineFixedCloseHour(hours.start, hours.end)
        
        if end != 23:
            end -= 2
        else:
            end -= 1
        
        results = {'opens': start, 'opens_min': hours.start.minute, 'closes': end, 'closes_min': hours.end.minute, 'past': past, 'closed':0}
        response = simplejson.dumps(results)
        return response

    
    
    
    
    def getAllDaysHours(self,date):
        d = date.split("-")
        dt = datetime.datetime(int(d[0]), int(d[1]), int(d[2]),0,0,0)
        hobj = HoursLookup(self.context)
        hours = hobj.getMainHoursForDate(dt)
        
        if hours.is_open:
            end = self.determineFixedCloseHour(hours.start,hours.end)
            response =  simplejson.dumps({'opens':hours.start.hour,'opens_min':hours.start.minute, 
                                          'closes':end, 'closes_min':hours.end.minute,'closed':0})
        else:
            response =  simplejson.dumps({'opens': 0, 'closes': 0, 'closed':1})
        return response


    def determineFixedCloseHour(self,start,end):
        if end.day > start.day or end.month > start.month or end.year > end.year:
            return 23
        else:
            return end.hour
            
            
            
            
            
            
            
            
            

    