# Print Class
#  - Will Print GroupFinder Events via PDF.
#
# Notes:
#  - PDF strings, lines, and rectangles are a nightmare to move.
#  - Editing PDF = Time Consuming.

from zope.interface import Interface

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from uwosh.librarygroupfinder.browser import util
from uwosh.librarygroupfinder.browser.locations import Locations

from operator import itemgetter, attrgetter

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from DateTime import DateTime
import datetime
from xml.dom import minidom

class IPrintMarker(Interface):
    """ Marker Interface """

class Print(BrowserView):

    DEFAULT_TABLE_LIMIT_SIZE = 21 #how many records to display in tables.
    printableSides = 1 # default one-sided print option

    def __call__(self):
    
        #Get Response
        response = self.request.response
        
        #Set response header to handle PDF
        response.setHeader('Content-Type', 'application/pdf')

        #Possible Parameters
        option = self.request.form.get('option', None)
        sides = self.request.form.get('sides', None)
        
        #Double Sided Printing?
        if sides == "2" or sides == "two" or sides == "two-sided":
            self.printableSides = 2
            
        #PDF Format
        if option == "office":
            return self.generateOfficePDF(response)
        elif option == "tables":
            return self.generateTablesPDF(response)
        elif option == "entrance":
            return self.generateEntrancePDF(response)
        
    
    def generateEntrancePDF(self,response):
        #Attach name.pdf file to responses content disposition
        response['Content-Disposition'] = 'attachment; filename=entrance.pdf'
        
        #Create empty pdf document, hook pdf with response
        pdf = Canvas(response)



        pdf.setFillColor(colors.black) #sets Line/Rectangle Colors
        pdf.roundRect(10, 755, 575, 75, 10, 1, 0)
        pdf.setFont("Helvetica-Bold", 40)
        pdf.setStrokeColorRGB(0, 0, 0) #sets Line/Rectangle Colors
        pdf.drawCentredString(300, 790, "GroupFinder")
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(15, 765, "The following spaces are reserved during scheduled hours")

        
        pdf.drawCentredString(300,725, datetime.datetime.now().strftime("%A, %B %d, %Y"))

        #Get Todays Events
        brains = sorted(util.gatherTodaysEvents(self), key=attrgetter('start','Title')) 
       
        index = 700
        i = 0
        for brain in brains:
            pdf.rect(45, index-30, 510, 42, stroke=1, fill=0) #Schedule List Rectangles
            if util.isPublic(self,brain.id):
                title = brain.Title
            else:
                title = "Private Group"
                
            pdf.setFont("Helvetica-Bold", 17)
            pdf.drawString(50, index-5, DateTime(brain.start).strftime("%I:%M %p").lower() +
                                        " - " + DateTime(brain.end).strftime("%I:%M %p").lower() +
                                        " : " + title)
            pdf.setFont("Helvetica", 17)
            l = self.locationLookup(brain.location)
            pdf.drawString(50, index-25, "Location: " + l['Name'] + " - " + l['DirectionsShort'])
            
            index -= 42
            i += 1
            if i == 13:
                pdf.setFont("Helvetica", 17)
                pdf.drawCentredString(300, index-5, "See Website For More Study Groups!")
                break
        
        pdf.setFont("Helvetica-Bold", 28)
        pdf.drawCentredString(300, 90, "Use GroupFinder to Reserve a Study Space.")
        pdf.setFont("Helvetica", 24)
        pdf.drawCentredString(300, 60, "http://www.uwosh.edu/library/groupfinder")
        
        pdf = self.tableFooter(pdf)
        
        pdf.showPage() #next page, finalize last page.
        pdf.save() #save the pdf content
        return response #return response with hooked pdf.
        
        
    
    
    
    def generateOfficePDF(self,response):
        #Attach name.pdf file to responses content disposition
        response['Content-Disposition'] = 'attachment; filename=office.pdf'
        
        #Create empty pdf document, hook pdf with response
        pdf = Canvas(response) 
        
        #Get Todays Events
        brains = sorted(util.gatherTodaysEvents(self), key=attrgetter('location')) #so awesome, sorts on any attribute!
        brains = sorted(brains, key=attrgetter('start')) #even better a secondary sort.
        
        #Header: Title Information and Settings
        pdf.setFont("Helvetica-Bold", 12)
        pdf.setStrokeColorRGB(0, 0, 0) #sets Line/Rectangle Colors
        
        #Header Left Title
        if brains != None and len(brains) > 0:
            pdf.drawString(15, 810, DateTime(brains[0].start).strftime("%A, %B %d, %Y") + " Schedule")
        else:
            pdf.drawString(15, 810, "No Groups scheduled for " + datetime.datetime.now().strftime("%A, %B %d, %Y"))
            
        #Header Right Title
        pdf.drawRightString(575, 810, "GroupFinder")
        
        #Body: List of Groups and Settings
        index = 792 #Pixel Index, starting at the top of the pdf page
        page = 1 #Page Number
        
        for brain in brains:
            pdf.setFont("Helvetica", 12)
            pdf.setStrokeColorRGB(0, 0, 0) #sets Line/Rectangle Colors
            pdf.rect(10, index-20, 575, 30, stroke=1, fill=0) #Rectangle around each Group
            pdf.drawString(15, index-3, brain.Title) #Group Description
            
            l = self.locationLookup(brain.location)
            pdf.drawString(15, index-15, DateTime(brain.start).strftime("%I:%M %p") + 
                                         " - " + DateTime(brain.end).strftime("%I:%M %p") +
                                         " in " + l['Name']) 
            index -= 30 #Move Pixel Index downwards
            
            #Reach Bottom of page?  Creates New Page.
            if index < 30:
                pdf.drawString(15, 5, "Page " + str(page))#add page number pages
                pdf.drawCentredString(300, 5, "Created on " + datetime.datetime.now().strftime("%m/%d/%Y at %I:%M %p"))
                page+=1
                index = 792
                pdf.showPage() #next page
        
        #add page number pages
        pdf.drawString(15, 5, "Page " + str(page))
        
        #add date PDF was created
        pdf.drawCentredString(300, 5, "Created on " + datetime.datetime.now().strftime("%m/%d/%Y at %I:%M %p"))
                        
        pdf.showPage() #next page, finalize last page.
        
        pdf.save() #save the pdf content
        return response #return response with hooked pdf.
    
    
    
    
    
    def generateTablesPDF(self, response):
        response['Content-Disposition'] = 'attachment; filename=tables.pdf'
        pdf = Canvas(response)
        pdf.setStrokeColorRGB(0, 0, 0)
        

        brains = sorted(util.gatherTodaysEvents(self), key=attrgetter('location','start')) 
        
        # Organize for Double-Sided Printing...
        prev = None
        mainArray = [] #init
        subArray = [] #init
        for brain in brains:
            if prev == brain.location:
                mainArray[len(mainArray)-1].append(brain)
            else:
                subArray = [] #reset list
                subArray.append(brain)
                mainArray.append(subArray)
            prev = brain.location #remember past
            
            
        # PDF Pages
        initPage = False
        for sarr in mainArray:
            
            #for Handles Two-Sided Pages!
            for j in range(self.printableSides):
                
                if initPage:
                    pdf.showPage()
                else:
                    initPage = True
                    
                l = self.locationLookup(sarr[0].location)
                
                # HEADER FOOTER ------------------------------------------------------------
                pdf = self.tableHeader(pdf,l['Name'],l['Description']) #Setup Header                
                pdf = self.tableInformation(pdf) #Setup Information
                pdf = self.tableLink(pdf)
                pdf = self.tableFooter(pdf) #Setup Footer
                index = 695 #reset index for new page
                i = 0 #Reset for new page
                

                pdf.setFont("Helvetica-Bold", 18)
                pdf.drawCentredString(300,715, datetime.datetime.now().strftime("%A, %B %d, %Y") + " Schedule")

                
                # BODY ------------------------------------------------------------
                for brain in sarr:
                    #Body: Schedule Side
                    pdf.rect(45, index-10, 510, 20, stroke=1, fill=0) #Schedule List Rectangles          
                    pdf.setFont("Helvetica", 17)
                    
                    if util.isPublic(self,brain.id):
                        title = brain.Title
                    else:
                        title = "Private Group"
                    
                    
                    pdf.drawString(50, index-5, DateTime(brain.start).strftime("%I:%M %p").lower() +
                                                " - " + DateTime(brain.end).strftime("%I:%M %p").lower() +
                                                " : " + title)
                    index -= 20     
                    i += 1
                    if i == self.DEFAULT_TABLE_LIMIT_SIZE:
                        pdf.drawCentredString(300, index-5, "More groups are scheduled after last posted time,")
                        pdf.drawCentredString(300, index-24, "please see Checkout and Reserves Desk.")
                        break
        pdf.showPage()
        pdf.save()
        return response
    
    

    #Table Format Header
    def tableHeader(self,pdf,location,description):
        
        pdf.setFont("Helvetica-Bold", 26)
        pdf.setStrokeColorRGB(0, 0, 0) #sets Line/Rectangle Colors
        pdf.drawCentredString(300, 795, "GroupFinder : " + location)
        
        #pdf.setFont("Helvetica", 14)
        #pdf = self.textCenteredWrap(pdf,description)
        
        
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawCentredString(300, 762, "This space is reserved during scheduled hours")
        
        pdf.setFillColor(colors.black) #sets Line/Rectangle Colors
        pdf.roundRect(10, 745, 575, 85, 10, 1, 0)
        return pdf    
    
    
    def textCenteredWrap(self,pdf,text):
        pdf.setFont("Helvetica", 12)
        lines = []
        i = 780
        if len(text) > 91:
            for c in text:
                lines.append(text[0:91])
                text = text[91:len(text)]
                if len(text) == 0:
                    break
            for l in lines:
                pdf.drawCentredString(300, i, l)
                i -= 12
        else:
            pdf.drawCentredString(300, i, text)
        self.leftOff = i
        return pdf
        
    #Table Format Footer
    def tableFooter(self,pdf):
        pdf.drawImage(self.context.absolute_url() + 
                      "/++resource++uwosh.librarygroupfinder.stylesheets/images/watermark.jpg",233,15,width=131,height=25)
        return pdf        
    
    
    
    def tableLink(self,pdf):
        pdf.setFont("Helvetica-Bold", 28)
        pdf.drawCentredString(300, 225, "Use GroupFinder To Reserve This Space.")
        pdf.setFont("Helvetica", 24)
        pdf.drawCentredString(300, 200, "http://www.uwosh.edu/library/groupfinder")
        return pdf
        
        
        
    #Table Format Information Box
    def tableInformation(self,pdf):
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(45,170, "Information") #Information Title
        
        pdf.setFont("Helvetica", 12)
        pdf.roundRect(45, 55, 510, 110, 10, stroke=1, fill=0) #Information Rectangle
        
        #Information 1) 2) 3) etc...
        pdf.drawString(50,145, "1) Scheduled study groups have rights to " +
                              "this area during their scheduled time.")
        pdf.drawString(50,125, "2) Study groups created today are not guaranteed a " +
                              "reservation.  To ensure a reservation")
        pdf.drawString(50,110, "the group must be scheduled prior to today.") #newline
        pdf.drawString(50,90, "3) Students, Tutors and Instructors can schedule a study group.")
        pdf.drawString(50,70, "4) Please visit the Checkout and Reserves Desk with any questions.")
        
        return pdf
        
        
    #Library WaterMark, instead of using image, this mimics the logo.
    def waterMark(self,pdf,x,y):
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(x, y, "Polk")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(x+30, y, "Library")
        return pdf
        
        
    def locationLookup(self,id):
        locations = Locations(self.context,self.request)
        location = locations.getLocationByUniqueId(id)
        if location != None:
             return location
        return None
