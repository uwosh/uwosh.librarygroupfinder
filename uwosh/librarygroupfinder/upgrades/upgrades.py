from Products.CMFCore.utils import getToolByName

import logging
logger = logging.getLogger("Update")

default_profile = 'profile-uwosh.librarygroupfinder:default'

def upgrade(upgrade_product,version):
    """ Decorator for updating the QuickInstaller of a upgrade """
    def wrap_func(fn):
        def wrap_func_args(context,*args):
            p = getToolByName(context,'portal_quickinstaller').get(upgrade_product)
            setattr(p,'installedversion',version)
            return fn(context,*args)
        return wrap_func_args
    return wrap_func



@upgrade('uwosh.librarygroupfinder','1.4.1')
def upgrade_to_1_4_1(context):
    pass

@upgrade('uwosh.librarygroupfinder','1.4.6')
def upgrade_to_1_4_6(context):
    logger.info( "upgrading to 1.4.6" )
    
@upgrade('uwosh.librarygroupfinder','1.5.0')
def upgrade_to_1_5_0(context):
    logger.info( "upgrading to 1.5.0" )

@upgrade('uwosh.librarygroupfinder','1.5.1')
def upgrade_to_1_5_1(context):
    logger.info( "upgrading to 1.5.1" )

@upgrade('uwosh.librarygroupfinder','1.5.2')
def upgrade_to_1_5_2(context):
    logger.info( "upgrading to 1.5.2" )
    
@upgrade('uwosh.librarygroupfinder','1.5.3')
def upgrade_to_1_5_3(context):
    logger.info( "upgrading to 1.5.3" )
    
@upgrade('uwosh.librarygroupfinder','1.5.4')
def upgrade_to_1_5_4(context):
    logger.info( "upgrading to 1.5.4" )
    
@upgrade('uwosh.librarygroupfinder','1.5.5')
def upgrade_to_1_5_5(context):
    logger.info( "upgrading to 1.5.5" )
    
@upgrade('uwosh.librarygroupfinder','1.5.6')
def upgrade_to_1_5_6(context):
    logger.info( "upgrading to 1.5.6" )
    
    from DateTime import DateTime 
    brains = context.portal_catalog.searchResults(portal_type='GroupFinderEvent')
    for brain in brains:
        obj = brain.getObject()
        start = str(brain.start).replace("GMT-5","US/CENTRAL").replace("GMT-6","US/CENTRAL")
        obj.setStartDate(DateTime(start))
    
        end= str(brain.end).replace("GMT-5","US/CENTRAL").replace("GMT-6","US/CENTRAL")
        obj.setEndDate(DateTime(end))
        logger.info( "PATCHING TIMES for " + brain.Title )
        obj.reindexObject()
        
@upgrade('uwosh.librarygroupfinder','1.5.7')
def upgrade_to_1_5_7(context):
    logger.info( "upgrading to 1.5.7" )
    
@upgrade('uwosh.librarygroupfinder','1.5.8')
def upgrade_to_1_5_8(context):
    logger.info( "upgrading to 1.5.8" )
    
@upgrade('uwosh.librarygroupfinder','1.5.9')
def upgrade_to_1_5_9(context):
    logger.info( "upgrading to 1.5.9" )   
    
    
    
    
    
    
    