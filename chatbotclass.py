#!/usr/bin/env python3


import random

class Chatbot:
    """The Chatbot class reads the script to get all keywords and possible responses. The keywords and responses are put into a navigateable dictionary. It takes the user input, standardizes the input, and finds the desired response to match the closest thing to the input."""
    
    def __init__(self,dataFile):
        '''This constructor creates a dictionary of possible responses from the database. It also creates empty lists and
        creates a dictionary of contraction replacements.'''
        
        #Creates empty keyList and dataDict dictionary
        keyList = []
        dataDict = {}
        
        dataList = dataFile.readlines() #opens databese and stores lines as a list
        
        i = 0 #initial line
        while i < len(dataList):
            if dataList[i][0] == "K": 
                dataDict[dataList[i][1:-1]] = [[],{}] #stores as keys in dictionary with values as list of an empty list and empty dictionary
                keyList.append(dataList[i][1:-1]) #adds to keyList
                i += 1

            elif dataList[i][0] == "R":
                if dataList[i-1][0] == "C": #decides if line before "R" line started with a "C"
                    dataDict[keyList[-1]][1][dataList[i-1][1:-1]] = [dataList[i][1:-1]] #stores line as value of inner dictionary and the key as the "C" line
                    i += 1
                    
                    isR = dataList[i][0] #looks at first character of following line
                    while isR == "R": #does this until first character is no longer "R"
                        dataDict[keyList[-1]][1][dataList[cIndex][1:-1]].append(dataList[i][1:-1]) #stores lines as value in list of inner dictionary and the key as the "C" line
                        i += 1
                        isR = dataList[i][0]
                        
                else:
                    dataDict[keyList[-1]][0].append(dataList[i][1:-1]) #If the previous line didd not start with "C"
                    i += 1
                    
            elif dataList[i][0] == "C": #If the line starts with "C", set the "cIndex" to that line
                cIndex = i
                i += 1

            else: #"#" filler line
                i += 1
                        

        self.dataDictionary = dataDict #saves dictionary as instance variable
        
        self.userKeyword = []
        self.dontRepeat =['perma']
        self.userResponseList = []

        contractionsFile = open("contractions.txt", "r")
        contractionsList = contractionsFile.readlines()
        self.contractionsDict = {}
        for line in contractionsList:
            lineList = line.split(",")
            self.contractionsDict[lineList[0].upper()] = lineList[1].upper() #creates dictionary where keys are contractions and values are replacements for contractions

    def formatUser(self, user):
        '''This method formats the text of the user by creating a capitalized version of the text without punctuation'''
        
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        empty = True
        for let in alphabet:
            if let in user.lower():
                empty = False

        if empty == False:
            if user[-1].lower() not in alphabet:
                user = user[:-1]
            user = user.upper()
            user = self.formatContractions(user)

        return user
        
    def editName(self, name):
        '''This method edits the input of the user's name and returns an edited version of the name'''
        
        name = name.split()
        wordnum = 0
        startname = 0
        actualname =''
        for word in name:
            if word == 'IS' or word == 'CALLED' or word == 'ME' or word == 'AM':
                startname = wordnum +1
            wordnum += 1
        
        for word in name[startname:]:
            actualname +=  word + " "
            
        self.name = actualname[:len(actualname)-1]
        return self.name


        
    def findKeyword(self,keyword):
        '''This function figures out which keyword matches or is the closest equivelent'''
        self.whatUserSaid = keyword
        
        #giving a response if nothing is given by the user
        if keyword == '':
            return"I'm really awkward so you are going to have to speak to keep this conversation going..." 
        else:
            
            if len(self.userKeyword) > 0: #if the keyword matches or is close enough to any of the topic responses
                self.requiredPercent = .4
                self.currentResponse = ''
                self.currentTopic = ''
                self.currentPercent = 0
                
                #runs through all possiblities of potential matches
                for itemK in reversed(self.userKeyword):
                    if self.requiredPercent <= 1:
                        for itemC in self.dataDictionary[itemK][1]: #checks if the keyword matches exactly
                            if itemC == keyword:
                                return self.chooseResponse(self.dataDictionary[itemK][1][itemC])

                            #finds the closest legal potential keyword
                            innerLayer = True
                            self.chooseClosestWord(keyword,itemC,innerLayer,itemK)

                    self.requiredPercent += .1
                  
                if self.currentPercent > 0: #if a keyword was found if it does it sends it to find its responses

                    return self.chooseResponse(self.dataDictionary[self.currentTopic][1][self.currentResponse])
                    
            #looks for exact match through whole dictionary of keywords
            for item in self.dataDictionary:
                if keyword == item:
                    self.userKeyword.append(item)
                    return self.chooseResponse(self.dataDictionary[item][0])
                 
            #looks for the closest match to the keyword
            self.currentResponse = ''
            self.currentPercent = 0
            filler = ''
            innerLayer = False
                
            for item in self.dataDictionary:
                self.chooseClosestWord(keyword,item,innerLayer,filler)
                    
                if self.currentPercent > .2:
                    self.userKeyword.append(self.currentResponse)
                    return self.chooseResponse(self.dataDictionary[self.currentResponse][0])
            
            #return if no keyword was found that was close enough and sees if the response repeats
            if self.userRepeat() == True:
                return "Please stop repeating yourself!!!"
            
            return "I'm sorry. I don't know what you are talking about."
            

    def chooseClosestWord(self,keyword,item,innerLayer,topic):
        '''scores the phrase on how close it is to what the user said '''
        kyword = keyword.split()
        keywordScore = 0
        for word in kyword:
            keywordScore += self.scoreWord(word,innerLayer)
            
        item2 = item.split()

        wordCount = 0
        if ('ARE' in kyword and 'YOU' in kyword) and ('ARE' in item2 and 'YOU' in item2): #checks for the order of "are" and "you" to determine if it is a question or a command
                        
            if kyword.index('ARE') > kyword.index('YOU') and item2.index('ARE') > item2.index('YOU'):
                wordCount += .3
                
            elif kyword.index('ARE') < kyword.index('YOU') and item2.index('ARE') < item2.index('YOU'):
                wordCount += .3

        for word in item2: #puts each word into scoreWord to score it; if it is not in the sentence it tries to account for plural words by taking away s's; the word's value is changed
            if word in kyword:
                amount = 1/kyword.count(word)
                wordCount += self.scoreWord(word,innerLayer)*amount
                
            elif word[-1] != 'S' and ((word + 'S') in kyword) and (word != "IS"):
                amount = 1/kyword.count(word + 'S')
                wordCount += (.9*amount)
                
        percent = wordCount/keywordScore #compares the percent of phrase correct to the current leader
        if innerLayer == True and percent > self.requiredPercent and percent > self.currentPercent:
            self.currentPercent = percent
            self.currentResponse = item
            self.currentTopic = topic
            
        elif innerLayer == False and percent > self.currentPercent:
            self.currentPercent = percent
            self.currentResponse = item
        
    def scoreWord(self,word,innerLayer):
        '''This function scores each indiviudal word'''
      
        #lists of common words, devalued words, and words that gain extra value when asking follow up questions
        devalued = ['what','why','how','which','where','now','soon','tommorow','today','yesterday', 'do']
        extraValue =['why','yes','no','what']
        commonWordList = ['to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'up', 'about', 'into', 'over', 'after', 'beneath', 'under', 'above', 'the', 'and', 'a', 'that', 'i', 'it', 'he', 'as', 'you', 'this', 'but', 'his', 'they', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their','is','are','like']
        
        if word.lower() in commonWordList:
            wordScore = .1
        
        elif innerLayer == True and word.lower() in extraValue:
            wordScore = 2
        elif word.lower() in devalued:
            wordScore = .6
        else:
            wordScore = 1

        return wordScore 
        
    def chooseResponse(self,responseList):
        #chooses the response based on the selected keyword
        response = 'perma'
        appear = 0
        
        #checks if it repeating itself
        if self.userRepeat() == True:
            return "Please stop repeating yourself!!!"

        #checks which potential answers it has used if all have been used it clears data so they can all be usede again
        else:
            for res in responseList:
                if res in self.dontRepeat:
                    appear += 1
            
            if appear == len(responseList):
                for res in responseList:
                    self.dontRepeat.remove(res)
                
            while response in self.dontRepeat:
                  #randomly chooses a response from the responses that it can choose inserts user's name when called upon
                  ranNum = random.randint(0, len(responseList)-1)
                  response = responseList[ranNum]
                  if "*name" in response:
                      response = responseList[ranNum].replace("*name", self.name)
  
            self.dontRepeat.append(response)
            return response

    def userRepeat(self):
        '''checks if the user has said the same thing three straight times'''
        
        self.userResponseList.append(self.whatUserSaid)
        if len(self.userResponseList) >= 3:
            if self.userResponseList[-1] == self.userResponseList[-2] and self.userResponseList[-2] == self.userResponseList[-3]:
                return True
        return False

    def formatContractions(self, sentence):
        '''converts all contractions to their alternative version'''
        newSentence = ""
        for word in sentence:
            if word in self.contractionsDict:
                newSentence += self.contractionsDict[word]
            else:
                newSentence += word

        return newSentence
