#from zope import schema 
#from zope.app.container.constraints import contains
#from zope.app.container.constraints import containers

from zope.interface import implements, directlyProvides, Interface
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base, folder, schemata
from Products.Archetypes.atapi import ImageField, ImageWidget, LinesField, LinesWidget

from Products.CMFCore.utils import getToolByName

from uwosh.librarygroupfinder import librarygroupfinderMessageFactory as _
from uwosh.librarygroupfinder.config import PROJECTNAME


class IGroupSpecialist(Interface):
    """ Interface """
    

"""
This is a basic Content type, one field for Class Type Referencing.
"""
GroupSpecialistSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((                                                                                              
    LinesField('listUsers',
        required=True,
        searchable=False,
        default = "",
        widget = LinesWidget(
            description = "Add specialists UWO email address (MUST BE UWO EMAIL, Example: bob123@uwosh.edu)  If you have over 50 specialist, please make another Group Specialist.",
            label = _(u'List of Specialists', default=u'List of Specialists')
        )
    ),                                                    
    ImageField('imageReference',
        required=False,
        searchable=False,
        default = "",
        validators = (),
        widget = ImageWidget(
            size=100,
            description = 'Upload a Specialist Image Icon',
            label = _(u'Specialist Image Icon', default=u'Specialist Image Icon'),
        )
    ),                                                                                                       
))




GroupSpecialistSchema['title'].widget.label = 'Group Specialist Title'
GroupSpecialistSchema['title'].widget.description = 'Group Specialists can be any group who specializes in helping.  (Tutors, Graduate Students, Writing Center Experts, etc...)'
GroupSpecialistSchema['description'].widget.description = 'This is shown as a ToolTip over the Image.'


GroupSpecialistSchema['title'].storage = atapi.AnnotationStorage()
GroupSpecialistSchema['description'].storage = atapi.AnnotationStorage()
GroupSpecialistSchema['listUsers'].storage = atapi.AnnotationStorage()
GroupSpecialistSchema['imageReference'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(GroupSpecialistSchema, moveDiscussion=False)


class GroupSpecialist(base.ATCTContent):
    """
    @author: David Hietpas
    @version: 1.1
    """
    
    implements(IGroupSpecialist)

    meta_type = "GroupSpecialist"
    schema = GroupSpecialistSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    
    
    def listUsers(self):
        """
        Returns a tuple listing of users for the Portal Catalog.
        @return: tuple
        """
        return self.getField('listUsers').get(self)


atapi.registerType(GroupSpecialist, PROJECTNAME)