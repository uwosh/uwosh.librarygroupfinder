# MainView Class
#  - The Homepage View which displays all events for users
#
# Notes:
#  - Works together with mainview.pt file

from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from uwosh.librarygroupfinder import librarygroupfinderMessageFactory as _
from uwosh.librarygroupfinder.interfaces.interfaces import IThemeSpecific
from uwosh.librarygroupfinder.browser.locations import Locations
from uwosh.librarygroupfinder.browser.attendees import Attendee
from uwosh.librarygroupfinder.browser.validator import Validation
from uwosh.librarygroupfinder.browser import util


from DateTime import DateTime
import datetime


class IMainViewMarker(Interface):
    """ Marker Interface """


class CommonView(BrowserView):
    
    def cacheNumber(self):
        now = datetime.datetime.now()
        return str(now.year)+str(now.month)+str(now.day)+str(now.hour)

 

class MainView(CommonView):
    implements(IThemeSpecific)
    template = ViewPageTemplateFile('templates/mainview.pt')

    # Controller, incoming handles requests
    def __call__(self):
        form = self.request.form
        
        validator = Validation()
        submit_button = form.get('form.button.Save', None) is not None    
        self.eventId = validator.isGroupFinderId(form,'form.id')
        
        if submit_button and validator.safeToProceed():
            response = self.removeEvent()
            if(response == True):
                return self.redirectMessager(u"Your Study Group has been cancelled.","Success","")
        else:
            return self.template()

    # Returns URL Object
    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    # Returns URL for the Create Button
    def createButtonLink(self):
        return  str(self.context.absolute_url()) + "/create"
    
    # Returns URL for the Staff Link
    def staffLink(self):
        return str(self.context.absolute_url()) + "/staff"
       
    # Returns URL for the About Button
    def aboutLink(self):
        return str(self.context.absolute_url()) +  "/about"
    
    # Returns URL for the Library Link BreadCrumb
    def libraryLink(self):
        return self.portal.absolute_url()
    
    # Calls util.py to build queries, also adds CSS class for "Today,Tomorrow,Upcoming" Labels. "mbar" is the yellow css bar.
    def getEvents(self):
        events = []
        events.append({"css":"gf_back_box_today","datecolor":"gf_bg_color","mbar":True,"events":self.setResponse(util.gatherTodaysEvents(self))})
        events.append({"css":"gf_back_box_tomorrow","datecolor":"gf_bg_color","mbar":True, "events":self.setResponse(util.gatherTomorrowsEvents(self))})
        events.append({"css":"gf_back_box_upcoming","datecolor":"","mbar":False, "events":self.setResponse(util.gatherUpcomingEvents(self))})
        return events

    # Sets and Formats Response for mainview.pt file
    def setResponse(self,brains):
        response = []
        locations = Locations(self.context,self.request)
        for brain in brains:
            location = locations.getLocationByUniqueId(brain.location)
            username = getToolByName(self.context, 'portal_membership').getAuthenticatedMember().getUserName()
            attendee = self.getAttendees(username,brain.id)
            
            if attendee['count'] == 1:
                attending = str(attendee['count']) + " Student Attending"
                removal = True
            else:
                attending = str(attendee['count']) + " Students Attending"
                removal = False
            if username == brain.listCreators[1]:
                creator = True
            else:
                creator = False

            response.append({'id': brain.id,
                             'Title': brain.Title,
                             'start': DateTime(brain.start).strftime("%I:%M %p"),
                             'end': " - " + DateTime(brain.end).strftime("%I:%M %p") + " at ",
                             'date': " on " + DateTime(brain.start).strftime("%b. %d, %Y"),
                             'location': location['Name'],
                             'locationId': brain.location,
                             'attendence': attending,
                             'alreadyAttending': attendee['signedup'],
                             'isCreator' : creator,
                             'isRemovable': removal,
                             'creatorMessage': 'Your Scheduled Group',
                             'isPublic': util.isPublic(self.context,brain.id),
                             'listCreators':  brain.listCreators
                            })
                            
        if len(response) == 0:
            return self.emptyResponse()
        else:
            return response
        
    # If query returns no results, this is the empty response   
    def emptyResponse(self):
        response = []
        response.append({'id': 'empty',
                     'Title': 'No Scheduled Study Groups',
                     'start': '',
                     'end': '',
                     'date': '',
                     'location': '',
                     'locationId': '',
                     'attendence': '',
                     'alreadyAttending': False,
                     'isCreator' : True,
                     'isRemovable': False,
                     'creatorMessage': '',
                     'isPublic': True,
                     'listCreators':  ''
                    })
        return response
    
    # Calls Attendee's Class and gets the List of Attending Users
    def getAttendees(self,username=None,id=None):
        result = {'count':0 , 'signedup':False}
        attendee = Attendee(self.context,self.request)
        attendees = attendee.getAttendees(id)
        result['count'] = len(attendees)
        for member in attendees:
            if member == username:
                result['signedup'] = True
        return result
    
    # Removes a GroupFinder Event.  Checks if user is Creator.
    def removeEvent(self):
        eid = self.eventId
        member =  getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
        brain = getToolByName(self.context, 'portal_catalog').searchResults(portal_type='GroupFinderEvent',id=eid,limit=1)
        creator = list(brain[0].listCreators)
        if member.getUserName() == creator[1]:
            util.delete_mover(self.context,self.request,brain[0].getObject())
            self.context.manage_delObjects([eid])
            return True
        return False
    
    # Redirects and Displays Message.
    def redirectMessager(self,message=u"Blank",intype="Info",location=""):
        IStatusMessage(self.request).addStatusMessage(_(message), type=intype)
        self.request.response.redirect(self.context.absolute_url() + location)
        return ''
    

    
    
    def isSpecialist(self,creators=""):
        """
        Finds and Marks if there is a group Specialist such as a Tutor or Staff Member.
        """
        self.getSpecialistIcon = ""
        self.getSpecialistTooltip = ""
        brains = getToolByName(self.context, 'portal_catalog').searchResults(portal_type='GroupSpecialist',
                                                                             path={'query':util.getGroupFinderPath(self.context),'depth':10})
        creator = ""
        if len(creators) > 1:
            creator = creators[1] + '@uwosh.edu'
        for brain in brains:
            l = list(brain.listUsers)
            for u in l:
                if u == creator:
                    self.getSpecialistIcon = '/'.join([brain.getURL(),'/imageReference'])
                    self.getSpecialistTooltip = brain.Description
                    return True
        return False



"""
For GroupFinder Event, all it does is disable the edit border.
"""
class EventView(BrowserView):
    implements(IThemeSpecific)
    template = ViewPageTemplateFile('templates/gfevent.pt')

    # Controller, incoming handles requests
    def __call__(self):
        self.request.set('disable_border', True)
        return self.template()