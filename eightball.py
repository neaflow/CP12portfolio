import random #we need this to select a random numbre
prevAns=0
while True:
    q = input("what's your question: ") #literally no purpose
    gotNewAns = 0
    while gotNewAns == 0:
        whichansCurrent = random.randint(0, 7) #which answer index
        
        
        answers=["Nope.", "Yup.", "Maybe.", "Probably.", "ask later.", "secret ending", "Absolutely", "Absolutely not"] #possible naswers
        if whichansCurrent != prevAns:
            print(answers[whichansCurrent]) #print the answer from its index
            gotNewAns = 1
            prevAns=whichansCurrent
