from zope.interface import implements, Interface
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from uwosh.librarygroupfinder import librarygroupfinderMessageFactory as _
from uwosh.librarygroupfinder.interfaces.interfaces import IThemeSpecific
from uwosh.librarygroupfinder.browser import util
from DateTime import DateTime

import smtplib
import socket

import logging
logger = logging.getLogger("GroupFinder")

class AutoEmailReminders(BrowserView):

    count = 0

    def __call__(self):
        try:
            self._execute()
            logger.info("Auto Emailer Reminder (Day-B4) - GOOD, email count " + str(self.count))
        except Exception as e:
            logger.error("Auto Emailer Reminder (Day-B4) - " + str(e))
        return "Sending"
    
    def _execute(self):
        self.count = 0
        if self.do_email_reminder():
            self._set_email_datestamp()
            self.send_reminder_email()

    def do_email_reminder(self):
        prop = getToolByName(self.context,'portal_properties').groupfinder_properties
        bool_email = prop.getProperty('email_reminder')
        str_date = prop.getProperty('email_reminder_executed_on')
        dt = DateTime(str_date)
        if DateTime().day() != dt.day() and bool_email:
            return True
        return False
    
    def _set_email_datestamp(self):
        props = getToolByName(self.context,'portal_properties').groupfinder_properties
        dt = str(DateTime())
        props.manage_changeProperties(email_reminder_executed_on=dt)
    
    def _send_email(self,mto,mfrom,subject,message):
        mh = getToolByName(self.context, 'MailHost')
        mh.send(message, mto=mto, mfrom=mfrom, subject=subject)
    
    def send_reminder_email(self):
        brains = util.gatherTomorrowsEvents(self)
        
        for brain in brains:
            self.count += 1
            ignore = brain.listCreators[0]
            creator = brain.listCreators[1]
            
            mto = creator + '@uwosh.edu'
            mfrom = 'librarytechnology@uwosh.edu'
            subject = "Study Group Reminder"
            message = "Tomorrow you have a study group scheduled. \n\n" \
                      "Title: " + brain.Title + "\n" \
                      "Start Time: " + DateTime(brain.start).aCommon() + "\n" \
                      "Location: " + self._get_location_info(brain.location) + "\n" \
                      "\nGroupFinder @ " + self.context.absolute_url()
            self._send_email(mto,mfrom,subject,message)

    def _get_location_info(self,uid):
        brains = getToolByName(self.context,'portal_catalog').searchResults(UID=uid,limit=1)
        if len(brains) > 0:
            obj = brains[0].getObject()
            return  obj.Title() + " - " + obj.getDirectionsFull()
        return "Please see schedule details."



""" 
Class below was created before knowledge of plone MailHost
=======================================================================
"""

# Emailer Class
#  - Builds a Email from inputs and sends it to given address.
#
# Notes:
#  - Setup for http://www.uwosh.edu systems

class Emailer:

    subject = None
    message = None
    from_email = None
    to_email = None

    def __init__(self,context,to_address=None):
        self.context = context
        self.to_email = to_address; #Set Default To Address
    
    # Sets Emails Parameters.  
    # Note:
    #  - This is done by building a String very specifically as done here.
    def setEmail(self,subject=None,message=None,from_email=None,to_email=None):
        self.subject = "Subject:" + subject + "\n" 
        self.message = message
        self.from_email = from_email
        
        if to_email != None:
            self.to_email = to_email
    
    # Sends Email to setup address
    # Determines how to send based if on LocalHost or on Test/Production Server.
    def sendEmail(self):
    
        if(getToolByName(self.context, 'portal_url').getPortalObject().absolute_url().find('localhost') > -1):
            s = smtplib.SMTP('out.mail.uwosh.edu', 25) #localhost server
        else:
            s = smtplib.SMTP('out.mail.uwosh.edu', 25) #prod and test server
        
        s.sendmail(self.from_email, [self.to_email], self.subject  + self.message)
        s.quit()
        
        #private final String MAIL_USER = "voyager"; //FOR PROD AND TEST SERVER
        #private final String MAIL_USER = "smtp.uwosh.edu"; //FOR LOCAL DEVELOPMENT
        #		props.put("mail.user", smtpUser); //FOR PROD AND TEST SERVER
        #		props.put("mail.smtp.host", smtpUser); //FOR LOCAL DEVELOPMENT