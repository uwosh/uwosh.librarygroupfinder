# FormView Class
#  - The Create Page View which allows the user to create a GroupFinder Event
#
# Notes:
#  - Works together with formview.pt file


from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from uwosh.librarygroupfinder import librarygroupfinderMessageFactory as _
from uwosh.librarygroupfinder.interfaces.interfaces import IThemeSpecific
from uwosh.librarygroupfinder.browser.validator import Validation

from uwosh.librarygroupfinder.browser.emailer import Emailer
from uwosh.librarygroupfinder.browser.staffview import GFEDAO
from uwosh.librarygroupfinder.browser.locations import Locations
from uwosh.librarygroupfinder.browser.mainview import CommonView

from Products.CMFPlone.utils import _createObjectByType

from DateTime import DateTime

import random

class IFormViewMarker(Interface):
    """ Marker for this view """

class FormView(CommonView):

    implements(IThemeSpecific)
    template = ViewPageTemplateFile('templates/formview.pt')
    
    GROUPFINDER_EMAIL = "Polk Library <polk-autoresponder@uwosh.edu>"
    
    # Controller for handling incoming requests
    def __call__(self):
        if getToolByName(self.context,'portal_membership').isAnonymousUser():
            self.request.response.redirect(self.portal.absolute_url() + 
                                           '/login_form?came_from=' + self.context.absolute_url() + '/create') 
        
        form = self.request.form
        self.request.set('disable_border', True)
        
        # Create Validation Object, validate all fields.
        validator = Validation()
        self.description = validator.isEmpty(form,'form.description')
        self.date = validator.isDate(form,'form.date')
        self.time = validator.isTime(form,'form.time')
        self.duration = validator.isDuration(form,'form.duration')
        self.location = validator.isEmpty(form,'form.location')
        self.isVisible = form.get('form.private', 'False')
        submitted = form.get('form.submitted', False)
        save_button = form.get('form.button.Save', None) is not None	
        cancel_button = form.get('form.button.Cancel', None) is not None	

        if submitted and save_button:		
            # If Validation Object is safe then proceed.
            if validator.safeToProceed():
                self.createGFEvent()
                return self.redirectMessager(u"Thank you for scheduling a study group, check your email for an invite to send to others.","Success",str(self.context.absolute_url()))
            else:
                return self.redirectMessager(u"All Fields are required, Thank you.","Note",str(self.context.absolute_url())+"/create")
        elif cancel_button:
            self.request.response.redirect(str(self.context.absolute_url()))
        else:
            return self.template()
            
	# Returns URL Object
    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    # Returns URL for the Homepage GroupFinder BreadCrumb
    def backLink(self):
        return str(self.context.absolute_url())
    
    # Returns URL for the Library Homepage BreadCrumb
    def libraryLink(self):
        return self.portal.absolute_url()
    
    def redirect(self):
        return  str('0; url=') + str(self.context.absolute_url()) + str('/login_form') 
        
    # Creates a GroupFinder Event and Saves to DB
    def createGFEvent(self):
        GFEDAO(self.context,self.request).create(self.description, 
                                                 self.location, 
                                                 self.date, 
                                                 self.time, 
                                                 self.duration, 
                                                 self.isVisible)
        
        # Emailer needs to know if Location Choosen needs to Notify Circulation Desk.
        groupfinder_properties = getToolByName(self.context, 'portal_properties').groupfinder_properties
        member = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
        locationObject = Locations(self.context,self.request)
        checkLocation = locationObject.getLocationByUniqueId(self.location)
        dt = DateTime(self.date + " " + self.time,datefmt="%Y-%m-%d %H:%M")
        if groupfinder_properties.getProperty('email_creator_on_creation'):
            self.emailReceipt(member=member,dt=dt,location=checkLocation)
     

    def emailCirculationDesk(self,member=None,dt=None,location=None):
        emailer = Emailer(self.context,getToolByName(self.context, 'portal_properties').site_properties.getProperty('circulations_email'))
        address = member.getUserName() + "@uwosh.edu" 
        email_message = ("Name - " + member.getProperty('fullname', 'Name Unavailable') +
                         "\nEmailAddress - " + address + 
                         "\nWhen - " + dt.aCommon() +
                         "\nRoom Choice - " + location +
                         "\n\n\n Reservation request was created through GroupFinder."
                         )
        emailer.setEmail(subject='WebMail - Reserve Group Study Room', message=email_message, from_email=address)
        emailer.sendEmail()


    # Emails the GroupFinder Event Creator
    #  - (Function probably can be moved to different class)
    def emailReceipt(self,member=None,dt=None,location=None):
        emailer = Emailer(self.context)
        address = self.GROUPFINDER_EMAIL
        to_address = member.getUserName() + "@uwosh.edu"
        email_message = ("Thank you for scheduling a study group through GroupFinder." +
                         "\n\nDo you want to notify your classmates?  Go to D2L @ https://uwosh.courses.wisconsin.edu/ and" +
                         " email the message below to your class." +
                         "\n\n---------------------------------------\n\n" +
                         "You have been invited to a study group at Polk Library." +
                         "\n\nGroup - " + self.description +
                         "\nDate - " + dt.aCommon() +
                         "\nLocation - " + location['Name'] +
                         "\nDirections - " + location['Directions'] +
                         "\n\nFor More Information Visit GroupFinder @ " + self.context.absolute_url()
                        )
        emailer.setEmail(subject='GroupFinder Receipt',
                         message=email_message,from_email=address,to_email=to_address)
        emailer.sendEmail()
        
    # Redirects and Displays Message.
    def redirectMessager(self,message=u"Blank",intype="Info",location=""):
        IStatusMessage(self.request).addStatusMessage(_(message), type=intype)
        self.request.response.redirect(location)
        return ''
    
    def _isPrivate(self):
        if self.isVisible == 'True':
            return '1'
        else:
            return '0'
        
        
        
        
        
        
        
        
        
        
        
        