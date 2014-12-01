# Use SetupHandler over profiles/default/STRUCTURE for custom installations.
# Much easier and more customizable

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

import os.path

# Custom Installer, setups up GroupFinder Contents
def install_setup(context):

    # ONLY INSTALL FOR THIS PRODUCT (This "If" statement is needed)
    if context.readDataFile('uwosh.librarygroupfinder_various.txt') is None:
            # Marker file not present, do not setup
            return


    print "GroupFinder Setup Starting."
    
    portal = context.getSite()

    setupFolderViews(portal,context)
    setupGroupFinderFolder(portal)
    checkAndCreateAboutPage(portal,context)
    #setupLocationXML(portal,context)
    setupStaffPrintPage(portal,context)
    setupStaffHelpPage(portal,context)
    
    
    setupLocations(portal,context)
    #migration(portal,context)
    
    
    
    print "GroupFinder Setup Finished."





def setupLocations(portal,context):
    existing = portal.groupfinder.objectIds()
    if "locations" in existing:
        pass
    else:
        print "Adding locations"
        create(portal.groupfinder,type='Folder',id='locations',title='Locations',description='')
        obj = portal.groupfinder.get('locations', None)
        obj.content_status_modify(workflow_action='publish')
        obj.reindexObject()
    
        create(portal.groupfinder.locations,type='GroupLocation',id='polk-101',title='Polk 101',description='')
        obj = portal.groupfinder.locations.get('polk-101', None)
        obj.content_status_modify(workflow_action='publish')
        obj.reindexObject()
        
        create(portal.groupfinder.locations,type='GroupLocation',id='jungle-table',title='Jungle Table',description='')
        obj = portal.groupfinder.locations.get('jungle-table', None)
        obj.content_status_modify(workflow_action='publish')
        obj.reindexObject()
        
        create(portal.groupfinder.locations,type='GroupLocation',id='table-with-a-view',title='Table With A View',description='')
        obj = portal.groupfinder.locations.get('table-with-a-view', None)
        obj.content_status_modify(workflow_action='publish')
        obj.reindexObject()
        
        create(portal.groupfinder.locations,type='GroupLocation',id='eagles-nest',title="Eagle's Nest",description='')
        obj = portal.groupfinder.locations.get('eagles-nest', None)
        obj.content_status_modify(workflow_action='publish')
        obj.reindexObject()
        
        create(portal.groupfinder.locations,type='GroupLocation',id='small-room',title='Small Room',description='')
        obj = portal.groupfinder.locations.get('small-room', None)
        obj.content_status_modify(workflow_action='publish')
        obj.reindexObject()
        
        create(portal.groupfinder.locations,type='GroupLocation',id='large-room',title='Large Room',description='')
        obj = portal.groupfinder.locations.get('large-room', None)
        obj.content_status_modify(workflow_action='publish')
        obj.reindexObject()
        

def migration(portal,context):
    objs = portal.groupfinder.listFolderContents(contentFilter={"portal_type" : "GroupFinderEvent"})
    for obj in objs:
        try:
            if obj.getLocation() == "Polk 101":
                obj.setLocation(portal.groupfinder.locations.get('polk-101', None).UID())
            if obj.getLocation() == "Jungle Table":
                obj.setLocation(portal.groupfinder.locations.get('jungle-table', None).UID())
            if obj.getLocation() == "Table With A View":
                obj.setLocation(portal.groupfinder.locations.get('table-with-a-view', None).UID())
            if obj.getLocation() == "Eagle's Nest":
                obj.setLocation(portal.groupfinder.locations.get('eagles-nest', None).UID())
            if obj.getLocation() == "Small Room":
                obj.setLocation(portal.groupfinder.locations.get('small-room', None).UID())
            if obj.getLocation() == "Large Room":
                obj.setLocation(portal.groupfinder.locations.get('large-room', None).UID())
            print "SUCCESS Migrated LOCATIONS: " + obj.Title() + " - " + obj.getId() + " - " + str(obj.getLocation())
        except Exception as e:
            print "FAIL Migrated LOCATIONS: " + obj.Title() + " - " + obj.getId() + " - " + str(obj.getLocation())
        obj.reindexObject()


def setupFolderViews(portal,context):
    viewListing = list(portal.portal_types.Folder.view_methods)
    found = False
    for view in viewListing:
        if view == 'groupfinder_homepage':
            found = True
    if not found:
        viewListing.append('groupfinder_homepage')
        portal.portal_types.Folder.view_methods = viewListing
        print "Added New Folder View."
        

def setupStaffPrintPage(portal,context):
    existing = portal.groupfinder.staff.objectIds()
    if "staff-printables" in existing:
        pass
    else:
        print "Added Staff Page."
        #Create Empty Page
        create(portal.groupfinder.staff,type='Document',id='staff-printables',title='Staff Printable Pages',description='')
        
        #Set Content of Empty Page
        doc = portal.groupfinder.staff.get('staff-printables', None)
        if doc != None:
            path = os.path.join(context._profile_path, 'staff-page.txt')

            doc.setText(str(open(path).read()))
            doc.reindexObject()


def setupStaffHelpPage(portal,context):
    existing = portal.groupfinder.staff.objectIds()
    if "staff-help" in existing:
        pass
    else:
        print "Added Staff Help Page."
        #Create Empty Page
        create(portal.groupfinder.staff,type='Document',id='staff-help',title='Staff Help Page',description='')
        
        #Set Content of Empty Page
        doc = portal.groupfinder.staff.get('staff-help', None)
        if doc != None:
            path = os.path.join(context._profile_path, 'staff-help.txt')

            doc.setText(str(open(path).read()))
            doc.reindexObject()


def setupLocationXML(portal,context):
    props = getToolByName(context, 'portal_properties')
    locationslist = props.site_properties.getProperty('locations_list')
    if len(locationslist) == 0:
        path = os.path.join(context._profile_path, 'location-list.txt')
        locations = str(open(path).read())
        props.site_properties.locations_list = locations
        print "Added Locations List to Site Properties."



def setupGroupFinderFolder(portal):
    existing = portal.objectIds()
    if "groupfinder" in existing:
        pass
    else:
        print "Added GroupFinder Folder."
        create(portal,type='Folder',id='groupfinder',title='GroupFinder',description='Folder for GroupFinder Events') 
        obj = portal.get('groupfinder', None)
        obj.content_status_modify(workflow_action='publish')
        obj.setConstrainTypesMode(1) # restrict what this folder can contain
        obj.setImmediatelyAddableTypes(['GroupFinderEvent','Document','GroupSpecialist'])
        obj.setLocallyAllowedTypes(['GroupFinderEvent','Document','GroupSpecialist'])
        #obj.setLayout('groupfinder_homepage')
        #obj.implements(IFormViewMarker)
        obj.reindexObject()
        setupStaffFolder(obj)



def setupStaffFolder(portal):
    existing = portal.objectIds()
    if "staff" in existing:
        pass
    else:
        print "Added Staff Folder."
        create(portal,type='Folder',id='staff',title='Staff',description='Folder for Staff Content') 
        obj = portal.get('staff', None)
        #obj.content_status_modify(workflow_action='publish')
        obj.setConstrainTypesMode(1) # restrict what this folder can contain
        obj.setImmediatelyAddableTypes(['Document'])
        obj.setLocallyAllowedTypes(['Document'])
        #obj.setLayout('staff_view')
        obj.reindexObject()
        

# Checks and Creates About Directory and Page if it doesn't exist
#  - Loads About Document from profiles/default/about-page.txt 
def checkAndCreateAboutPage(portal,context):
    existing = portal.groupfinder.objectIds()
    if "about" in existing:
        pass
    else:
        print "Added About Page."
        #Create Empty Page
        create(portal.groupfinder,type='Document',id='about',title='About GroupFinder',description='About Page')
        
        #Set Content of Empty Page
        doc = portal.groupfinder.get('about', None)
        if doc != None:
            path = os.path.join(context._profile_path, 'about-page.txt')

            doc.setText(str(open(path).read()))
            doc.content_status_modify(workflow_action='publish')
            doc.reindexObject()



# Create Method for setting up any type of Content
def create(portal,type=None,id=None,title=None,description=None):
        _createObjectByType(type, portal, id=id, title=title,
                            description=description)
        obj = portal.get(id, None)
        obj.reindexObject()
          
        