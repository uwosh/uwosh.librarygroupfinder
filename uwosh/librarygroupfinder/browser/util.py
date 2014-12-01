from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from DateTime import DateTime
import datetime


# Queries the DB for a GroupFinder Event.
def queryEvents(self,qdate = ['1960','12','25'],inStart=None,inEnd=None):
    """ PLEASE USE queryEventsSimple()!!!! """
    if(inStart == None and inEnd == None):
        start = DateTime(int(qdate[0]),int(qdate[1]),int(qdate[2]),0,0,0)
        end = DateTime(int(qdate[0]),int(qdate[1]),int(qdate[2]),23,59,59)
    else:
        start = inStart
        end = inEnd
    catalog = getToolByName(self, 'portal_catalog')
    
    gf_path = getToolByName(self.context, 'portal_properties').base_paths.getProperty('base_groupfinder_path')
    path = {'query':gf_path,'depth':1}
    
    return catalog.searchResults(portal_type='GroupFinderEvent',path=path,start={"query":[start,end],"range":"minmax"},sort_on='start')


def queryEventsSimple(context,start,end):
    """ USE THIS OVER queryEvents() """
    catalog = getToolByName(context, 'portal_catalog')
    gf_path = getToolByName(context, 'portal_properties').base_paths.getProperty('base_groupfinder_path')
    path = {'query':gf_path,'depth':1}  
    return catalog.searchResults(portal_type='GroupFinderEvent',path=path,start={"query":[start,end],"range":"minmax"},sort_on='start')




# Sets up query to the DB and gathers today's events
def gatherTodaysEvents(self):
    fDate = str(datetime.date.today()).split("-")
    return queryEvents(self,qdate = fDate)

# Sets up query to the DB and gathers tomorrows's events
def gatherTomorrowsEvents(self):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    fDate = str(tomorrow).split("-")
    return queryEvents(self,qdate = fDate)

# Sets up query to the DB and gathers upcoming events
def gatherUpcomingEvents(self):
    upcomingStart = datetime.date.today() + datetime.timedelta(days=2)
    fDate1 = str(upcomingStart).split("-")
    start = DateTime(int(fDate1[0]),int(fDate1[1]),int(fDate1[2]),0,0,0)
    
    upcomingEnd = datetime.date.today() + datetime.timedelta(days=365)
    fDate2 = str(upcomingEnd).split("-")
    end = DateTime(int(fDate2[0]),int(fDate2[1]),int(fDate2[2]),23,59,59)
    
    return queryEvents(self,inStart=start,inEnd=end)

# GETS ALL EVENTS
def getAllUpcomingEvents(self):
    upcomingStart = datetime.date.today() + datetime.timedelta()
    fDate1 = str(upcomingStart).split("-")
    start = DateTime(int(fDate1[0]),int(fDate1[1]),int(fDate1[2]),0,0,0)
    upcomingEnd = datetime.date.today() + datetime.timedelta(days=30)
    fDate2 = str(upcomingEnd).split("-")
    end = DateTime(int(fDate2[0]),int(fDate2[1]),int(fDate2[2]),23,59,59)
    return queryEvents(self,inStart=start,inEnd=end)



def getStartDate(self,date):
    pass

def getEndDate(self,date):
    pass

def getGroupFinderPath(self):
    props = getToolByName(self, 'portal_properties')
    return props.base_paths.getProperty('base_groupfinder_path')

def getGroupFinderBaseObject(self):
    gfpath = getGroupFinderPath(self)
    brains = getToolByName(self, 'portal_catalog').searchResults(path={'query':gfpath,'depth':0})
    if len(brains) == 0:
        return None
    return brains[0].getObject()


def getStartDate(date):
    fDate = date.split("-")
    return DateTime(int(fDate[0]),int(fDate[1]),int(fDate[2]),0,0,0)

def getEndDate(date):
    fDate = date.split("-")
    return DateTime(int(fDate[0]),int(fDate[1]),int(fDate[2]),23,59,59)

def isPublic(self,id):
    i = id.rsplit('-')
    if i[6] == '1':
        return True
    else:
        return False

def translate_GroupLocation(brain):
    try:
        brain.groupLocation = {'building':brain.groupLocation[0],'extraNotes':brain.groupLocation[1],'keyRequired':brain.groupLocation[2],
                'maxGroups':brain.groupLocation[3],'capacity':brain.groupLocation[4],'roomContents':brain.groupLocation[5],
                'directions':brain.groupLocation[6],'directions_full':brain.groupLocation[7]}
        return brain
    except Exception as e:
        print str(e)
        return {}
    
def delete_mover(context,request,del_obj):
    gf_base = getToolByName(context,"portal_properties").base_paths.getProperty('base_groupfinder_path')
    gf_delete_bin = gf_base + '/bin'
    brains = getToolByName(context,"portal_catalog").searchResults(portal_type='Folder',id='bin',path={'query':gf_delete_bin,'depth':0})
    delete_bin = brains[0].getObject()
    
    # Move to new location
    _createObjectByType("GroupFinderEvent", delete_bin, id=del_obj.id, title=del_obj.title,location=del_obj.location)
    obj = delete_bin.get(del_obj.id, None)
    obj.setCreators(del_obj.listCreators())
    obj.setAttendees(del_obj.getAttendees())
    obj.setStartDate(del_obj.start())
    obj.setEndDate(del_obj.end())
    obj.reindexObject()
    
    
    
    
    