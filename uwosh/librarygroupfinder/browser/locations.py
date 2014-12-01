# Locations Class
#  - Reads Location information from a properities field in site_properities
#  - Locations are saved from xml file to site_properities on install.
#
# Notes:
#  - Not a 'pretty' coded class.  I had many DB Date Range query issues.  

from Products.CMFCore.utils import getToolByName

from uwosh.librarygroupfinder.browser.validator import Validation
from uwosh.librarygroupfinder.browser import util
from operator import itemgetter
from DateTime import DateTime
import time
import datetime
import simplejson

class Locations:

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    # Controller for incoming Requests
    def __call__(self):
        form = self.request.form
        self.brains = []
        self.takenLocations = []
        self.response = []
        
        validators = Validation()
        date = validators.isDate(form,'date')
        mytime = validators.isTime(form,'time')
        duration = validators.isDuration(form,'duration')
        getAll = form.get('option',False)
        
        if(getAll == "all"):
            self.getAllLocations()
        elif(validators.safeToProceed()):
            self.getBrains(date)
            self.findScheduledLocations(date,mytime,duration)
            self.getAvailableLocations()
            
        return simplejson.dumps({'response' : self.response})

    # Returns URL Object
    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    # Get all GroupFinder Events for Given Parameters.
    def getBrains(self,date):
        start = util.getStartDate(date)
        end = util.getEndDate(date)
        gf_base = getToolByName(self.context,"portal_properties").base_paths.getProperty('base_groupfinder_path')
        path = {'query':gf_base,'depth':1}
        self.brains = getToolByName(self.context, 'portal_catalog').searchResults(portal_type='GroupFinderEvent',path=path,start={"query":[start,end],"range":"minmax"})
    
    # Compare incoming parameters (the new event) to the current DB events. 
    # If time/date is NOT available for incoming parameters (the new event) add to taken locations.
    def findScheduledLocations(self,date,my_time,duration):
        tmp = datetime.datetime.strptime(date + " " + my_time, "%Y-%m-%d %H:%M")
        #print "START " + str(tmp)
        desiredStartTime = time.mktime(tmp.timetuple())
        
        
        tmp = datetime.datetime.strptime(date + " " + my_time, "%Y-%m-%d %H:%M")
        tmp = tmp + datetime.timedelta(minutes=int(duration))
        #print "END " + str(tmp)
        desiredEndTime = time.mktime(tmp.timetuple())
        
        for brain in self.brains:
            format = str(brain.start).split(" ")
            start = self.getTimeStamp(format[0] + " " +  format[1])
            format = str(brain.end).split(" ")
            end = self.getTimeStamp(format[0] + " " + format[1])
            if(((start <= desiredStartTime and desiredStartTime < end) or (start < desiredEndTime and desiredEndTime <= end)) or (desiredStartTime < start and end < desiredEndTime)):
                self.takenLocations.append(brain)

    # Custom Format to TimeStamp
    # Note:
    #  - date parameter format: "%Y-%m-%d %H:%M:%S"  (aka 2010-01-24 14:59:59)
    def getTimeStamp(self,date):
        time_tuple = time.strptime(str(date), "%Y/%m/%d %H:%M:%S")
        return time.mktime(time_tuple)
    
    # Show all locations that are not taken.
    def getAvailableLocations(self):    
        brains = self.getLocationBrains()
        
        for brain in brains:
            brain = util.translate_GroupLocation(brain)
            count = 0
            for taken in self.takenLocations:
                if brain.UID == taken.location:
                    count = count + 1
            if count < int(brain.groupLocation['maxGroups']) or count == 0:
                self.buildResponse(brain)
    
    # Get all Location Brains.
    def getLocationBrains(self):
        return getToolByName(self.context, 'portal_catalog').searchResults(portal_type='GroupLocation',
                                                                           path={'query':util.getGroupFinderPath(self.context),'depth':10},
                                                                           sort_on="getObjPositionInParent")
    
    # Get and Display All Locations regardless if taken or not.
    def getAllLocations(self):
        self.response = []
        brains = self.getLocationBrains()
        for brain in brains:
            self.buildResponse(util.translate_GroupLocation(brain))

    # Get and Display Location by Unique ID.
    def getLocationByUniqueId(self,id):
        self.response = []
        brains = self.getLocationBrains()
        for brain in brains:
            if id == brain.UID:
                self.buildResponse(util.translate_GroupLocation(brain))
                return self.response[0]
        return None
    
    # Get and Display Location Name by Unique ID.
    def getLocationNameByUniqueId(self,id):
        brains = self.getLocationBrains()
        for brain in brains:
            if id == brain.UID:
                return brain.Title
        return None
        
    # Sets and Formats Response
    def buildResponse(self,brain):
        self.response.append({  "Id" : brain.id,
                                "UID" : brain.UID,
                                "Name" : brain.Title,
                                "Description" : brain.Description,
                                "Capacity" : brain.groupLocation['capacity'],
                                "RoomContents" : self.listToString(brain.groupLocation['roomContents']),
                                "ImageURL" : brain.getURL() + "/imageReference",
                                "Directions" : brain.groupLocation['directions_full'],
                                "DirectionsShort" : brain.groupLocation['directions'],
                                "Key" : brain.groupLocation['keyRequired'],
                                "MaxGroups" : brain.groupLocation['maxGroups'],
                                "Note" : brain.groupLocation['extraNotes'],
                             })
    
    def listToString(self,listing):
        listing = list(listing)
        return ', '.join(listing)
    
    
    def __str__(self):
        return self.response
                                