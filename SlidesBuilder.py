# A tool for building a simple Google Slides

# You need credentials.json in the same directory in order to run this code

# Setup
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/presentations'

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('slides', 'v1', http=creds.authorize(Http()))

print("OK!")

import random as rnd

UW_PURPLE = (51, 0, 111)
UW_METALLIC_GOLD = (145, 123, 76)

class Presentation:
    
    # Construct a presentation
    def __init__(self, pid = None, title = None, debug = False):
        self.DEBUG_MODE = debug
        if pid == None:
            # Create a new Presentation
            self.presentation = service.presentations().create(body = {"title" : title}).execute()
        else:
            self.presentation = service.presentations().get(presentationId = pid).execute()
        self.MY_ID = self.presentation["presentationId"]
        self.PENDING = [] # Clear Pending List
        self.checkSlide()
        
        
    # Execute Everything in the queue
    def run(self):
        if len(self.PENDING) == 0:
            return
        if self.DEBUG_MODE:
            print("%d command was sent." % (len(self.PENDING)))
        service.presentations().batchUpdate(presentationId = self.MY_ID, body = {"requests" : self.PENDING}).execute()
        if self.DEBUG_MODE:
            print("Done!")
        self.checkSlide()
        self.PENDING = [] # Clear Pending List
     
    # Debug
    def __str__(self):
        return "[%s] (Id: %s), Slide Count: %d" % (self.presentation["title"], self.MY_ID, len(self.slideSet))
    
    def checkSlide(self):
        self.slideSet = set([])
        for slide in self.presentation["slides"]:
            self.slideSet.add(slide["objectId"])
    
    # (Immediately) Set (override) the text of an object
    def generalTextSetter(self, objectId, targetText):
        self.run()
        try:
            pending1 = { "requests": [ {"deleteText": {"objectId": objectId}}] }
            service.presentations().batchUpdate(presentationId = self.MY_ID, body = pending1).execute()
        except:
            pass
        pending2 = { "requests": [ {"insertText": {"objectId": objectId, "text": targetText} }] }
        service.presentations().batchUpdate(presentationId = self.MY_ID, body = pending2).execute()
        
    # FOLLOWING FUNCTIONS WILL ADD REQUESTS TO THE QUEUE
    
    def deleteText(self, objectId):
        self.PENDING.append({"deleteText": {"objectId": objectId}})
        
    def insertText(self, objectId, targetText):
        self.PENDING.append({"insertText": {"objectId": objectId, "text": targetText}})
        
    def lazyTextSetter(self, objectId, targetText):
        self.deleteText(objectId)
        self.insertText(objectId, targetText)
    
    # Text formatting on a specific object
    def generalTextFormatting(self, objectId, color = None, bold = False, italic = False, underline = False,
                             font = None, fontSize = None, strikethrough = False):
        cur = {"bold": bold, "italic": italic, "underline": underline, "strikethrough": strikethrough}
        if fontSize:
            cur["fontSize"] = {"magnitude": fontSize, "unit": "PT"}
        if font:
            cur["fontFamily"] = font
        if color:
            col = {"red": color[0]/256, "green": color[1]/256, "blue": color[2]/256}
            cur["foregroundColor"] = {"opaqueColor": {"rgbColor": col}}
        self.PENDING.append({"updateTextStyle": {"objectId": objectId, "style": cur, "fields": "*"}})
    
    
    # IMMEDIATELY Set Title on the first page
    def setTitle(self, title):
        self.generalTextSetter("i0", title)
    
    # IMMEDIATELY Set Subtitle on the first page
    def setSubtitle(self, subtitle):
        self.generalTextSetter("i1", subtitle)
        
        
    # Immediately Create a template for "card" slides (if not exist)
    def createTemplatePage(self):
        if "template" in self.slideSet:
            return
        pending = {"requests": [{"duplicateObject": {"objectId": "p", "objectIds": {
          "p": "template", "i0": "templateTitle", "i1": "templateSubtitle"}}}]}
        self.run()
        service.presentations().batchUpdate(presentationId = self.MY_ID, body = pending).execute()
        self.checkSlide()
    
    # Return a random string of length l
    def getRandomString(self, l = 8):
        ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
        s = ""
        for i in range(l):
            s += rnd.choice(ALPHABET)
        return s
    
    # Add a card to a presentation
    def addCard(self, title = "", subtitle = ""):
        targetPage = self.getRandomString()
        while targetPage in self.slideSet:
            targetPage = self.getRandomString()
        # Find new Id for them
        titleBox = targetPage + "Title"
        subtitleBox = targetPage + "Subtitle"
        
        # Build a request to copy
        self.PENDING.append({"duplicateObject": {"objectId": "template", "objectIds": {
          "template": targetPage, "templateTitle": titleBox, "templateSubtitle": subtitleBox}}})
        
        # Fill out words
        
        self.lazyTextSetter(titleBox, title)
        self.lazyTextSetter(subtitleBox, subtitle)
        
        
    # General Remove
    def generalRemove(self, objectId):
        self.PENDING.append({"deleteObject": {"objectId": objectId}})
        
    # Remove Template
    def removeTemplate(self):
        self.generalRemove("template")

class DeckBuilder:
    
    def __init__(self, fileName, wordList, headTitle = "Word List", subtitle = ""):
        print("Building %s" % (headTitle))
        self.PRESENTATION = Presentation(title = fileName)
        self.PRESENTATION.setTitle(headTitle)
        self.PRESENTATION.setSubtitle(subtitle)
        self.PRESENTATION.generalTextFormatting("i0", color = UW_PURPLE, bold = True, font = "Encode Sans", fontSize = 72)
        self.PRESENTATION.generalTextFormatting("i1", font = "Encode Sans")
        self.PRESENTATION.createTemplatePage()
        self.PRESENTATION.generalTextFormatting("templateTitle", color = UW_PURPLE, bold = True, font = "Encode Sans", fontSize = 96)
        self.PRESENTATION.generalTextFormatting("i0", color = UW_METALLIC_GOLD, bold = True, font = "Encode Sans", fontSize = 72)
        for word in wordList:
            self.PRESENTATION.addCard(title = word)
        self.PRESENTATION.removeTemplate()
        self.PRESENTATION.run()
        print("Done!")
        
    def __str__(self):
        return str(self.PRESENTATION)