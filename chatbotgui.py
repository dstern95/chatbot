#!/usr/bin/env python3


from tkinter import *
from chatbotclass import *
import subprocess
import time
import datetime

class ChatbotGUI(Frame):
    '''This class creates a GUI for the chatbotclass with label text, an entry field, a text box, and a quit button'''
    def __init__(self,master):
        Frame.__init__(self, master)
        fin = open('script.txt', 'r')
        self.grid()
        self.config(bg = '#e7cdac') #creates background color
        
        self.createWidgets() #loads widgets
        self.friend = Chatbot(fin) #calls chatbotclass
        
        self.userText = '' #sets user text to empty

    def createWidgets(self):
        '''This function displays the widgets needed in the GUI.
        Input: widget types
        Return: GUI layout'''
        
        #Creates the header that tells the user to talk to the chatbot (centered at top)
        self.header = Label(self, text="Talk to S.I.R.!", font="Impact 16 bold italic", fg = "#475f83")
        self.header.config(bg = "#e7cdac")
        self.header.grid(row=0, sticky=EW)

        #Creates textbox that will display the conversation. The text box is initialized as uneditable
        self.chatbotResponse = Text(self)
        self.chatbotResponse.config(bg = '#80c6e7')
        self.chatbotResponse.grid(row=2, pady = 5, padx = 5)
        self.chatbotResponse.config(state=DISABLED)

        #Creates an entry field that tracks the cursor to keep current text in field
        self.userEntry = Entry(self)
        self.userEntry.config(width=30)
        self.userEntry.grid(row=1,sticky=W, padx = 5)
        self.userEntry.scan_dragto(-1)

        #Creates starting text in text field. The user will respond to the question posed by the chatbot
        self.chatbotResponse.config(state=NORMAL)
        response = "Hello my name is S.I.R.(Speaking Intelligent Robot). What is your name?"
        self.chatbotResponse.insert(END, "S.I.R.: " + response +"\n")
        self.chatbotResponse.config(state=DISABLED)
        self.userEntry.bind("<Return>", self.submitEntry)
        
        #Creates quit button that closes the window
        self.quitChatbot = Button(self, text="GOODBYE", fg = "#475f83", activeforeground="#e36968",activebackground = "#ffffff",  command=self.closeWindow)
        self.quitChatbot.config(bg = "#ffffff")
        self.quitChatbot.grid(row=3, sticky=W, padx = 5)

        imageList = ["gifs/frame0.gif", "gifs/frame1.gif", "gifs/frame2.gif", "gifs/frame3.gif", "gifs/frame4.gif", "gifs/frame5.gif", "gifs/frame6.gif"] #Image list of robot GIF frames

        #creates a canvas that will hold the frames
        photo = PhotoImage(file=imageList[0])
        self.width = photo.width()
        self.height = photo.height()
        self.canvas = Canvas(width=self.width, height=self.height, highlightthickness=0)
        self.canvas.config(bg = "#e7cdac")
        self.canvas.grid()
        
        #Creates list of photoImages of the imageList
        self.gifList = []
        for imageFile in imageList:
            photo = PhotoImage(file=imageFile)
            self.gifList.append(photo)
            
    def closeWindow(self):
        '''This function saves the conversation log found in the text field and saves it to a text file. The window is then closed
        Input: conversation (conversation log), Button press
        Return: conversation log'''
        
        conversation = self.chatbotResponse.get('1.0', 'end-1c')
        now = datetime.datetime.now()
        conversationFile = open("conversationLog_" + str(now), "w") #conversation log file named by the current date and time
        conversationFile.write(conversation)
        conversationFile.close()
        
        self.master.destroy() #closes window

    def submitEntry(self, event):
        '''This function takes the text from the user and finds the appropriate response from the list of responses'''
        
        response = "S.I.R.: Hello my name is S.I.R.(Speaking Intelligent Robot). What is your name?\n" #Initial text in field
        if self.chatbotResponse.get('1.0', 'end-1c') == response: #occurs if the user has not said anything yet
            name = self.friend.formatUser(self.userEntry.get())
            self.userText = self.friend.editName(name)
            text = "You: " + self.userEntry.get() + "\n" #gets the name from the user
            
            self.chatbotResponse.config(state=NORMAL)
            self.chatbotResponse.insert(END, text)
            self.chatbotResponse.config(state=DISABLED)
            self.chatbotResponse.see(END)
            self.userEntry.delete(0,END)
            
            response = "Hello " + self.userText + ", It is nice to meet you."
            self.displayResponse(response) #responds to user's name
            self.runningImage()
        else: #occurs after the user has entered their name
            self.userText = self.friend.formatUser(self.userEntry.get())
            text = "You: " + self.userEntry.get() + "\n" #Displays user text in text field
            
            self.chatbotResponse.config(state=NORMAL)
            self.chatbotResponse.insert(END, text)
            self.chatbotResponse.config(state=DISABLED)
            self.chatbotResponse.see(END)
            self.userEntry.delete(0,END)
            
            response = self.friend.findKeyword(self.userText) #fubds response to user's text
            self.displayResponse(response)
            
            self.runningImage()

    def displayResponse(self, response):
        '''This function displays the response of the chatbot and uses text-to-speech to make response audible'''
        
        self.chatbotResponse.config(state=NORMAL) #displays the response in text field
        self.chatbotResponse.insert(END, "S.I.R.: " + response +"\n")
        self.chatbotResponse.config(state=DISABLED)
        self.chatbotResponse.see(END)
        
        subprocess.Popen(["espeak", "-v", "en", response]) #runs text-to-speech
        
        self.runningImage() #calls runningImage function

    def runningImage(self):
        '''This function goes through the list of photoImages and displays and deletes them for two cycles'''
        
        for i in range(0,2):
            for gif in self.gifList:
                self.canvas.delete(ALL) #deletes previous image
                self.canvas.create_image(self.width/2.0, self.height/2.0, image=gif) #displays new frame
                self.canvas.update()
                time.sleep(0.1) #waits 0.1 seconds
