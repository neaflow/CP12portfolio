import random #we need this to select a random numbre
import time
prevAns=0
print("------------------------------------------")
kindOfAnswers=["normal", "optimistic", "pessimistic", "unsure"]
gaveAkindOfAnswer=0
type = "placeholder"
while gaveAkindOfAnswer==0:
    print("types of answers:")
    for answer in kindOfAnswers:
        print(answer)
    print("------------------------------------------")
    type = input("which kind of answer do you want? ")
    if type in kindOfAnswers:
        gaveAkindOfAnswer=1
    else:
        print("------------------------------------------")
        print("that's not a correct answer. do it better.")
        



while True:
    print("------------------------------------------")
    q = input("what's your question: ") #literally no purpose
    gotNewAns = 0
    while gotNewAns == 0:
        whichansCurrent = random.randint(0, 7) #which answer index
        
        if type == "normal":
            answers=["Nope.", "Yup.", "Maybe.", "Probably.", "ask later.", "secret ending", "Absolutely", "Absolutely not"] #possible naswers
        if type == "optimistic":
            answers=["yeah!.", "Yup.", "sure.", "Probably.", "ask later and i will tell you YES!", "secret ending", "Absolutely", "Absolutely 2.0"] #possible naswers
        if type == "pessimistic":
            answers=["Nope.", "nah.", "don't think so.", "Probably not.", "ask later and i will say NO.", "secret ending", "obviously not", "Absolutely not"] #possible naswers
        if type == "unsure":
            answers=["don't know.", "unsure.", "Maybe.", "can't tell.", "outlook unstable.", "secret ending", "potentially", "couldn't tell you"] #possible naswers
        if whichansCurrent != prevAns:
            print("------------------------------------------")
            print("thinking......")
            time.sleep(4)
            print(answers[whichansCurrent]) #print the answer from its index
            gotNewAns = 1
            prevAns=whichansCurrent
            time.sleep(2)
