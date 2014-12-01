#from zope import schema 
#from zope.app.container.constraints import contains
#from zope.app.container.constraints import containers

from zope.interface import implements, directlyProvides, Interface
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base, folder, schemata
from Products.Archetypes.atapi import TextField, TextAreaWidget, SelectionWidget, StringField, StringWidget, ImageField, ImageWidget, LinesField, LinesWidget

from Products.CMFCore.utils import getToolByName

from uwosh.librarygroupfinder import librarygroupfinderMessageFactory as _
from uwosh.librarygroupfinder.config import PROJECTNAME


class IGroupLocation(Interface):
    """ Interface """
    

"""
This is a basic Content type, one field for Class Type Referencing.
"""
GroupLocationSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((                                                                                              

    StringField('building',
        required=True,
        searchable=False,
        default = "",
        widget = StringWidget(
            description = "Building name where the location is located.",
            label = _(u'Building Name', default=u'Building Name')
        )
    ),     

    StringField('directions',
        required=False,
        searchable=False,
        default = "",
        widget = StringWidget(
            description = "One-Line Short Description of Directions",
            label = _(u'Quick Directions', default=u'Quick Directions')
        )
    ),        
                                                                          
    StringField('directions_full',
        required=True,
        searchable=False,
        default = "",
        widget = StringWidget(
            description = "Full Description of Directions",
            label = _(u'Full Directions', default=u'Full Directions')
        )
    ),   
                                                                          

    StringField('keyRequired',
        required=True,
        searchable=False,
        default = "0",
        vocabulary = [("No","No"),("Yes","Yes")],
        widget = SelectionWidget(
            description = "Is there a key required for this specific location?",
            label = _(u'Is a key required?', default=u'Is a key required?'),
            format = 'select'
        )
    ), 

                                                          
    StringField('maxGroups',
        required=True,
        searchable=False,
        default = "1",
        widget = StringWidget(
            description = "Max Number of Groups allowed in that location at 1 time.",
            label = _(u'Max Number of Groups', default=u'Max Number of Groups')
        )
    ),                                                                         
                                                                       
    StringField('capacity',
        required=True,
        searchable=False,
        default = "*",
        widget = StringWidget(
            description = "Max Capacity of the area. * For no limit.",
            label = _(u'Area Max Capacity', default=u'Area Max Capacity')
        )
    ),             
                  
    LinesField('roomContents',
        required=True,
        searchable=False,
        default = "",
        widget = LinesWidget(
            description = "List what the room contents for working materials, one per line.",
            label = _(u'Room Contents', default=u'Room Contents')
        )
    ),           
                  
    TextField('extraNotes',
        required=False,
        searchable=False,
        default = "",
        widget = TextAreaWidget(
            description = "This note is displayed with area as a extra snippet of information.",
            label = _(u'Extra Note', default=u'Extra Note')
        )
    ),   
                                                                                                      
                                                                                                                             
    ImageField('imageReference',
        required=False,
        searchable=False,
        default = "",
        validators = (),
        widget = ImageWidget(
            size=100,
            description = 'Upload a image of the location.',
            label = _(u'Location Image', default=u'Location Image'),
        )
    ),                                                                                                       
))




GroupLocationSchema['title'].widget.label = 'Location Name'
GroupLocationSchema['description'].widget.label = "Description of what the Location Name means"

GroupLocationSchema['title'].storage = atapi.AnnotationStorage()
GroupLocationSchema['description'].storage = atapi.AnnotationStorage()
GroupLocationSchema['building'].storage = atapi.AnnotationStorage()
GroupLocationSchema['extraNotes'].storage = atapi.AnnotationStorage()
GroupLocationSchema['keyRequired'].storage = atapi.AnnotationStorage()
GroupLocationSchema['maxGroups'].storage = atapi.AnnotationStorage()
GroupLocationSchema['capacity'].storage = atapi.AnnotationStorage()
GroupLocationSchema['roomContents'].storage = atapi.AnnotationStorage()
GroupLocationSchema['directions'].storage = atapi.AnnotationStorage()
GroupLocationSchema['directions_full'].storage = atapi.AnnotationStorage()
GroupLocationSchema['imageReference'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(GroupLocationSchema, moveDiscussion=False)


class GroupLocation(base.ATCTContent):
    """
    @author: David Hietpas
    @version: 1.1
    """
    
    implements(IGroupLocation)

    meta_type = "GroupLocation"
    schema = GroupLocationSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')


    def groupLocation(self):
        """
        Used for one-stop cataloging.
        - To translate, use util.translate_GroupLocation(arg)
        """
        return tuple([self.getBuilding(),self.getExtraNotes(),self.getKeyRequired(),self.getMaxGroups(),
                      self.getCapacity(),self.getRoomContents(),self.getDirections(),self.getDirectionsFull()
                    ])


    def getDirectionsFull(self):
        return self.getField('directions_full').get(self)

atapi.registerType(GroupLocation, PROJECTNAME)