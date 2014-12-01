# Validation Class
#  - Basic Validations for GroupFinder Product.
#  - Most Validations are for custom formats

from Products.CMFCore.utils import getToolByName
import re

class Validation:

    def __init__(self):
        self.error = 0
    
    # Determine if Date is Valid and a Valid format.
    def isDate(self, form, name):
        value = form.get(name,'').strip()
        if (re.match("20[0-2][0-9]-[0-1][0-9]-[0-3][0-9]", value) != None):
            return value
        self.error = 1
    
    # Determine if Time is Valid and a Valid format.
    def isTime(self, form, name):
        value = form.get(name,'').strip()
        if (re.match("([0-2])?[0-9]:[0-9][0-9]", value) != None):
            return value
        self.error = 2
    
    # Determine if Duration is Valid and a Valid format.
    def isDuration(self, form, name):
        allowed = ['30','60','90','120']
        value = form.get(name,'0').strip()
        if value in allowed:
            return value
        self.error = 3
    
    # Determine if String is Valid and a Valid format.
    def isEmpty(self, form, name):
        value = form.get(name,'').strip()
        if (value != ""):
            return value
        self.error = 4
    
    # Determine if GroupFinder ID is Valid and a Valid format.
    #  - GroupFinder ID's are unique
    # GroupFinderID Format >>> gf-event-2010-08-31-7501
    def isGroupFinderId(self, form, name):
        value = form.get(name,'').strip()
        if (re.match("gf-event-([0-9])+-([0-9])+-([0-9])+-([0-9])+", value) != None):
            return value
        self.error = 5
    
    # Return Error Code   
    def getError(self):
        return str(self.error)
    
    # IF no error occurred during validation, it is safe to submit.
    #  - This setup allows the validation of all Fields through one screening.
    def safeToProceed(self):
        if self.error == 0:
            return True
        else:
            return False
            
    def __str__(self):
        return "Error ID: " + str(self.error)