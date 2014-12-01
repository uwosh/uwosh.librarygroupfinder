# Creates the GroupFinderEvent by Extending ATEvent

#from zope import schema
from zope.interface import Interface
#from zope.app.container.constraints import contains
#from zope.app.container.constraints import containers

from zope.interface import implements, directlyProvides
from Products.Archetypes import atapi
from Products.ATContentTypes.content import event, base, schemata

from uwosh.librarygroupfinder.config import PROJECTNAME

class IGroupFinderEvent(Interface):
    """a form to request a query"""

GFESchema = event.ATEvent.schema.copy() + atapi.Schema(( ))

GFESchema['title'].storage = atapi.AnnotationStorage()
GFESchema['description'].storage = atapi.AnnotationStorage()

GFESchema['title'].widget.label = 'Group Finder Event'
GFESchema['description'].widget.description = 'Event designed for only Group Finder'
GFESchema['description'].required = True

schemata.finalizeATCTSchema(GFESchema, moveDiscussion=False)
GFESchema.changeSchemataForField('relatedItems', 'default')


class GroupFinderEvent(base.ATCTContent, event.ATEvent):
    """Project Request Form"""
    implements(IGroupFinderEvent)

    meta_type = "GroupFinderEvent"
    schema = GFESchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
        
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    
atapi.registerType(GroupFinderEvent, PROJECTNAME)
