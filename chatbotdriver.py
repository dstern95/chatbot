#!/usr/bin/env python3


from tkinter import *
from chatbotgui import *

def main():
    '''This main function creates the Tkinter window with a specified size and background color that holds the chatbotGUI'''
    
    root = Tk()
    root.title("Welcome to S.I.R!") #window label text
    root.geometry("577x1080") #window dimensions
    root.config(bg = "#e7cdac") #window background color
    chatbot = ChatbotGUI(root) #call to chatbot GUI

    root.mainloop()

main()
