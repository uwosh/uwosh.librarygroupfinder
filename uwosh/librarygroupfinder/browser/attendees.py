# Attendees Class
#  - Sets and Removes Attends for a GroupFinder Event

from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from uwosh.librarygroupfinder import librarygroupfinderMessageFactory as _
from uwosh.librarygroupfinder.interfaces.interfaces import IThemeSpecific
from uwosh.librarygroupfinder.browser.validator import Validation

from DateTime import DateTime
import datetime
import simplejson

class Attendee:

    # Final Return Response
    response = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    # Controller for handling requests
    def __call__(self):
        form = self.request.form

        validator = Validation()
        self.eventId = validator.isGroupFinderId(form,'id')
        self.option = form.get('option','')
        
        if self.getUserName() == "Anonymous User":
            self.response = {"success" : "2"}
        elif self.option == "set" and validator.safeToProceed():
            self.setAttendee()
        elif self.option == "remove" and validator.safeToProceed():
            self.removeAttendee()
        else:
            self.response = {"error" : "option not provided"}
        
        return simplejson.dumps({'response' : self.response})        
    
    # User calling setAttendee() will set their attendence in the group
    def setAttendee(self):
        try:
            obj = self.getEvent().getObject()
            listing = list(obj.getAttendees())
            listing.append(self.getUserName())
            count = len(listing)
            obj.setAttendees(tuple(listing))
            self.response = {"success" : "1" , "count" : str(count)}
        except ValueError:
            self.response = {"success" : "0"}
            
    # User calling removeAttendee() will remove their attendence in the group
    def removeAttendee(self):
        try:
            obj = self.getEvent().getObject()
            listing = list(obj.getAttendees())
            listing2 = []
            for attendee in listing:
                if attendee != self.getUserName():
                    listing2.append(attendee)
            obj.setAttendees(tuple(listing2))
            self.response = {"success" : "1" , "count" : str(len(listing2))}
        except ValueError:
            self.response = {"success" : "0"}
    
    # Will get All Attendees for a specific GroupFinder Event
    # id: GroupFinder Unique ID
    # returns: List of Attendees
    def getAttendees(self,id):
        response = { 'count' : 0 , 'found' : False }
        obj = self.getEvent(id).getObject()
        return list(obj.getAttendees())
        
    # Will get specific GroupFinder Event
    # eid: GroupFinder Unique ID
    # returns: GroupFinder Event
    def getEvent(self, eid = None):
        if eid == None:
            eid = self.eventId
        brain = getToolByName(self.context, 'portal_catalog').searchResults(portal_type='GroupFinderEvent',id=eid,limit=1)
        return brain[0]

    # Will get the Authenticated Username
    # returns: Active Users name
    def getUserName(self):
        member = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
        return str(member.getUserName())
        
    def __str__(self):
        return self.response