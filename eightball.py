import random #we need this to select a random numbre
q = input("what's your question: ") #literally no purpose
whichans = random.randint(0, 7) #which answer index
answers=["Nope.", "Yup.", "Maybe.", "Probably.", "ask later.", "secret ending", "Absolutely", "Absolutely not"] #possible naswers
print(answers[whichans]) #print the answer from its index
