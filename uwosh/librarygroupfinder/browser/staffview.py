from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from OFS import ObjectManager

from uwosh.librarygroupfinder import librarygroupfinderMessageFactory as _
from uwosh.librarygroupfinder.interfaces.interfaces import IThemeSpecific
from uwosh.librarygroupfinder.browser.locations import Locations
from uwosh.librarygroupfinder.browser.attendees import Attendee
from uwosh.librarygroupfinder.browser.validator import Validation
from uwosh.librarygroupfinder.browser import util
from uwosh.librarygroupfinder.browser.mainview import CommonView

from Products.CMFPlone.utils import _createObjectByType

from DateTime import DateTime
from operator import itemgetter
import simplejson
import datetime
import time
import random
import Acquisition


import logging

logger = logging.getLogger("TEST")

class GFEDAO:
    def __init__(self,context,request):
        self.context = context
        self.request = request

    def create(self,description,location_uid,date,time,duration,private,member=None):
        
        if getToolByName(self.context, 'portal_membership').isAnonymousUser():
            return self.template()
        
        if private == 'True':
            private  = '1'
        else:
            private  = '0'
        
        id = str(random.randint(1, 10000))
        eid = "gf-event-"+date+"-"+id+"-"+private
        
        if len(description) > 40:
            description = description[0:40] + "..."
        
        # Time Setup
        fTime = time.split(":")
        start = DateTime(date + " " + time + " US/CENTRAL")
        end = DateTime(start)
        tmp = end.asdatetime() + datetime.timedelta(minutes=int(duration))
        end = DateTime(tmp)
        
        #_createObjectByType bypasses permission security.
        _createObjectByType("GroupFinderEvent", self.context, id=eid, title=description, location=location_uid)
        obj = self.context.get(eid, None)
        
        obj.setTitle(description)
        obj.setLocation(location_uid)
        
        if member == None:
            member = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
            obj.setCreators(["Confidential",member.getUserName(),member.getUserName()])
            obj.setAttendees(member.getUserName())
        else:
            name = member.split('@')
            staff = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
            obj.setCreators(["Staff",name[0],staff.getUserName()])
            obj.setAttendees(name[0])
        obj.setStartDate(start)
        obj.setEndDate(end)
        obj.reindexObject()
        
        
        
class BookingViewInfo(CommonView):
    implements(IThemeSpecific)
    template = ViewPageTemplateFile('templates/booking_info.pt')
    
    def __call__(self):
        self.id = self.request.form.get('id','0')
        self.remove = self.request.form.get('remove','0')
        self.date = self.request.form.get('date','')
        if self.id == '0':
            return ""
        elif self.id != '0' and self.remove == '1':
            self.delete_gfevent()
            if self.date != '':
                return self.redirectMessager(u"Group was removed.","Success",str(self.context.absolute_url()+"/staff?=date"+self.date))
            return self.redirectMessager(u"Group was removed.","Success",str(self.context.absolute_url()+"/staff"))
        else:
            return self.template()
    
    def delete_gfevent(self):
        brains = getToolByName(self.context,'portal_catalog').searchResults(portal_type="GroupFinderEvent",id=self.id)
        obj = brains[0].getObject()
        parent = obj.aq_parent
        if obj != None:
            if obj.portal_type == 'GroupFinderEvent':
                util.delete_mover(self.context, self.request, obj)
                parent._delObject(self.id)
                parent.reindexObject()
        
    def getInfo(self):
        return getToolByName(self.context,'portal_catalog').searchResults(portal_type="GroupFinderEvent",id=self.id)
        
    def isMod(self):
        try:
            path = getToolByName(self.context,'portal_properties').base_paths.getProperty('base_groupfinder_path')
            brains = getToolByName(self.context,'portal_catalog').searchResults(portal_type="Folder",
                                                                                path={'query':path,'depth':1},
                                                                                id='staff')
            if len(brains) > 0:
                staff_obj = brains[0].getObject()
                return (self.context.portal_membership.checkPermission('Add portal content', staff_obj) or
                        self.context.portal_membership.checkPermission('Modify portal content', staff_obj) or
                        self.context.portal_membership.checkPermission('Review portal content', staff_obj) or
                        self.context.portal_membership.checkPermission('View', staff_obj))
        except:
            print "idMod Error"
            pass
        return False
        
    def format(self,dt):
        return DateTime(dt).aCommon()
    
    def getRequester(self,creators):
        try:
            return creators[1] + "@uwosh.edu"
        except:
            return ""
    def getCreator(self,creators):
        try:
            return creators[2] + "@uwosh.edu"
        except:
            return ""
        
    def getTitle(self,id,title):
        if id.endswith("-0"):
            return "Private Event"
        return title
    
    def redirectMessager(self,message=u"Blank",intype="Info",location=""):
        IStatusMessage(self.request).addStatusMessage(_(message), type=intype)
        self.request.response.redirect(location)
        return ''
    
    def bypass_cache(self):
        return random.random()       
    
    
        
class IBookingViewMarker(Interface):
    """ Marker Interface """

class BookingView(CommonView):
    implements(IThemeSpecific)

    def __call__(self):
        self.date = self.request.form.get('date','None')
        bool_locations = self.request.form.get('locations','0')
        bool_groups = self.request.form.get('groups','0')
        s_ts = float(self.request.form.get('s_ts','0'))
        e_ts = float(self.request.form.get('e_ts','0'))
        
        if bool_locations == '1':
            self.request.response.setHeader('Content-Type', 'application/json')
            return simplejson.dumps(self.get_locations())
        elif bool_groups == '1':
            self.request.response.setHeader('Content-Type', 'application/json')
            return simplejson.dumps(self.get_groups(s_ts,e_ts))
        else:
            return self.template()
    
    
    def get_date_from_create(self):
        if self.date != "None":
            return self.date
        return self.today()
    
    def get_groups(self,start_ts,end_ts):
        start = DateTime(datetime.datetime.fromtimestamp(start_ts))
        end = DateTime(datetime.datetime.fromtimestamp(end_ts))
        brains = util.queryEventsSimple(self.context,start,end)
        results = []
        for brain in brains:
            results.append({'Title':brain.Title,
                            'id':brain.id,
                            'start':self.toTS(DateTime(brain.start)),
                            'end':self.toTS(DateTime(brain.end)),
                            'location':brain.location
                            })
        return {'response':results}

    def get_locations(self):
        brains = getToolByName(self.context, 'portal_catalog').searchResults(portal_type='GroupLocation',
                                                                             sort_on='getObjPositionInParent')
        results = []
        for brain in brains:
            brain = util.translate_GroupLocation(brain)
            results.append({'Title':brain.Title,'UID':brain.UID,'directions':brain.groupLocation['directions']})
        return {'response':results}

    def toTS(self,dt):
        return dt.timeTime()    
        
    def today(self):
        return DateTime().strftime("%Y-%m-%d")

class BookingSubView(BookingView):
    implements(IThemeSpecific)
    template = ViewPageTemplateFile('templates/booking_subview.pt')

class BookingMainView(BookingView):
    implements(IThemeSpecific)
    template = ViewPageTemplateFile('templates/booking_view.pt')
        
        
        
class IStaffViewMarker(Interface):
    """ Marker Interface """

class StaffView(CommonView):
    implements(IThemeSpecific)
    template = ViewPageTemplateFile('templates/staffview.pt')

    
    def __call__(self):
        form = self.request.form
        
        validator = Validation()
        self.email = validator.isEmpty(form,'form.email')
        self.description = validator.isEmpty(form,'form.description')
        self.date = validator.isDate(form,'form.date')
        self.time = validator.isTime(form,'form.start')
        self.duration = validator.isDuration(form,'form.end')
        self.location = validator.isEmpty(form,'form.location')
        self.isVisible = form.get('form.private', 'False')
        
        self.deleteItem = form.get('form.remove','')
        self.id = form.get('form.id','')
        
        self.params = ""
        if str(self.date) != "None" and self.date != '':
            self.params = "?date="+self.date
            
        if self.id != '' and self.deleteItem == '1':
            #self.removeGFEvent()
            self.delete_gfevent()
            return self.redirectMessager(u"Group Removed Successfully.","Success",str(self.context.absolute_url()))
            
        
        if form.get('form.submission', '') == "1" and validator.safeToProceed():
            obj = util.getGroupFinderBaseObject(self)
            GFEDAO(obj,self.request).create(self.description, 
                                                     self.location, 
                                                     self.date, 
                                                     self.time, 
                                                     self.duration, 
                                                     self.isVisible, 
                                                     member=self.email)
            return self.redirectMessager(u"Group was scheduled.","Success",str(self.context.absolute_url() + self.params))
        elif form.get('form.submission', '') == "1" and not validator.safeToProceed():
            return self.redirectMessager(u"All Fields are required, Thank you.","Error",str(self.context.absolute_url()))
        return self.template()
    
    
    def delete_gfevent(self):
        parent = self.context.aq_parent
        obj = parent.get(self.id, None)
        if obj != None:
            if obj.portal_type == 'GroupFinderEvent':
                util.delete_mover(self.context, self.request, obj)
                parent._delObject(self.id)
                parent.reindexObject()
    
    # Returns URL for the Homepage GroupFinder BreadCrumb, will be REMOVED later with new theme
    def backLink(self):
        base_path = getToolByName(self.context, 'portal_properties').base_paths.getProperty('base_groupfinder_path')
        brains = getToolByName(self.context, 'portal_catalog').searchResults(id="groupfinder", path={'query':base_path,'depth':0})
        if len(brains) > 0:
            return brains[0].getURL()
        else:
            return "http://www.uwosh.edu/library/groupfinder" #tmp fallback
        
    
                
    # Returns URL Object
    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def today(self):
        return DateTime().strftime("%Y-%m-%d")
    
    
    
    def redirectMessager(self,message=u"Blank",intype="Info",location=""):
        IStatusMessage(self.request).addStatusMessage(_(message), type=intype)
        self.request.response.redirect(location)
        return ''
    
    
    
    
class IStaffSubViewMarker(Interface):
    """ Marker Interface """
    
class SubViewStaffListing(CommonView):
    implements(IThemeSpecific)
    template = ViewPageTemplateFile('templates/subview_gfstaff.pt')
    
    

    def __call__(self):
        form = self.request.form
        date = form.get('form.date', None)
        
        if date == None:
            self.date = None
        else:
            self.date = date

        return self.template()
    

    def getAllGFEvents(self):
        if self.date == None:
            dt = datetime.datetime.now()
            start = DateTime(dt.year,dt.month,dt.day,0,0,0)
            end = DateTime(dt.year,dt.month,dt.day,23,59,59)
        else:
            d = self.date.split("-")
            start = util.getStartDate(self.date)
            end =  util.getEndDate(self.date)
        return self.queryEvents(start,end)
    
    def queryEvents(self,start=None,end=None):      
        gf_base = getToolByName(self.context,"portal_properties").base_paths.getProperty('base_groupfinder_path')
        path = {'query':gf_base,'depth':1}
        brains = getToolByName(self.context, 'portal_catalog').searchResults(portal_type='GroupFinderEvent',path=path,start={"query":[start,end], "range":"minmax"})
        brains = sorted(brains,key=itemgetter('location','start'))
        results = []
        prev = None
        locations = Locations(self.context,self.request)
        
        for brain in brains:
            css = 'border-top-width: 1px;'
            start = DateTime(brain.start).strftime("%I:%M %p")
            end = DateTime(brain.end).strftime("%I:%M %p")
            
            if brain.location != prev and prev != None:
                css = 'border-top-width: 4px;'
            prev = brain.location
            results.append({'id':brain.id,'Title':brain.Title,
                            'location':locations.getLocationNameByUniqueId(brain.location),
                            'start':start, 
                            'end':end,
                            'requester':brain.listCreators[1],
                            'has_creator_info':self._has_creator_name(brain),
                            'creator':self._get_creator_name(brain),
                            'created': self._format_date(brain.created),
                            'css':css
                            })
        return results
    
    
    
    def _format_date(self,dt):
        dt = DateTime(dt)
        return dt.strftime("%b. %d %Y at %I:%M %p")
    
    
    def _get_creator_name(self,brain):
        if self._has_creator_name(brain):
            return brain.listCreators[2]
        return "Unknown"
    
    
    def _has_creator_name(self,brain):
        creators = list(brain.listCreators)
        if len(creators) <= 2:
            return False
        return True
            
            
    
    def isPublic(self,id):
        return util.isPublic(self,id)
        
    
    def getLink(self):
        return str(util.getGroupFinderBaseObject(self.context).absolute_url())
    

    