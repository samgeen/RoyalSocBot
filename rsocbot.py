'''
Writes amendments to the US constititon
Sam Geen & Mike Cook, August 2014
'''

import Image
import string, os, random
#import chooser
#from templates import templates
#from websters import websters
import twython
from twython import Twython
from secrets import *
import pymarkovchain

capitalise = False

xelatex = "xelatex"

def strippunc(instring):
    '''
    Strips punctuation from the input string
    '''
    return instring.translate(string.maketrans("",""), string.punctuation)

def ordinal(i):
    '''
    Totally not ripped off of stackoverflow >_>
    '''
    k=i%10
    return"%d%s"%(i,"tsnrhtdd"[(i/10%10!=1)*(k<4)*k::4])

def subwordindict(word):
    for entry in websters.iterkeys():
        if entry in word:
            # HACK FOR SPECIAL CASE
            if entry == "VERB":
                if "VERBTGTED" in word:
                    return "VERBTGTED"
            return entry
    return ""

def parse(instring):
    # Should have used a class OH WELL
    global websters
    global capitalise
    word = strippunc(instring)
    # Turn on/off capitalisation
    if word == "CAP":
        capitalise = True
        return ""
    if word == "NOCAP":
        capitalise = False
        return ""
    # Is an entry in websters in the word?
    entry = subwordindict(word)
    if entry:
        # Choose from list if this is a keyword
        output = chooser.choice(websters[entry])
        # Capitalise?
        if capitalise:
            output = ' '.join(entry[0].upper() + entry[1:] for \
                                  entry in output.split())
        websters["SAME"] = [output]
    else:
        # Not a special keyword?
        output = instring
    # If we had any punctuation left over, put it back in
    if entry:
        output = instring.replace(entry,output)
    return output

def runfortemplate(template):
    output = ordinal(chooser.choice(range(0,100)))+" :"
    # Parse the template word by word to fill in keywords
    for item in template.split(" "):
        output += " "+parse(item)
    lout = len(output)
    # Diagnostic character count (disabled for release mode)
    #output += " ("+str(lout)+")"
    # Get rid of double spaces
    output = ' '.join(output.split())
    return output

def maketex(text):
    bw,bh = 1280,854 # HARD CODED HACK!
    template = open("template.tex","r").read()
    out = template.replace("REPLACEME",text)
    open("scratch.tex","w").write(out)
    os.system(xelatex+" scratch.tex")
    os.system("convert -density 300 scratch.pdf -trim test.png")
    os.system("convert test.png -bordercolor none -border 10 -fuzz 10% -transparent white test.png")
    im = Image.open("test.png")
    tw,th = im.size
    x = random.randint(0,bw-tw)
    y = random.randint(0,bh-th)
    tw = str(tw)
    th = str(th)
    x = str(x)
    y = str(y)
    os.system("convert oldpage.png -crop "+tw+"x"+th+"+"+x+"+"+y+
              " croppage.png")
    os.system("composite -gravity West test.png croppage.png output.png")

def makemarkov():
    os.system("rm ./markov")
    mc = pymarkovchain.MarkovChain("./markov")
    text = open("royalsociety.txt").read().replace("/n"," ")
    text = text.replace("Mr.", "Mr")
    text = text.replace("Dr.", "Dr")
    text = text.replace("{","\{")
    text = text.replace("}","\}")
    text = text.replace("&","\&")
    mc.generateDatabase(text,sentenceSep="[.?]")
    return mc

def maketweet(mc):
    return mc.generateString()
    
def skimparens(text):
    '''
    Closes and cleans up parentheses
    '''
    nest = 0
    op = "("
    cl = ")"
    for i in range(0,len(text)):
        if text[i] == op:
            nest += 1
        if text[i] == cl:
            if nest == 0:
                temp = list(text)
                temp[i] = op[0]
                text = "".join(temp)
                nest += 1
            else:
                nest -= 1
    while nest > 0:
        text += cl+" "
        nest -= 1
    return text

def run():
    mc = makemarkov()
    tweet = "a"
    while len(tweet) < 200 or tweet[0].islower():
        tweet =  maketweet(mc)
    tweet = skimparens(tweet)
    tweet += "."
    print tweet
    maketex(tweet)
    # Yes it is, but justin case
    if len(tweet) > 140:
        tweet = tweet[:100]+"..."
    print tweet, len(tweet)
    # Set up twitter
    #twitter = twython.Twython(twitter_token,twitter_secret,access_token,access_secret)
    # Pick a template to use
    #template = chooser.choice(templates)
    #tweet = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaargh" # yes
    #while len(tweet) > 140:
    #    tweet =  runfortemplate(template)
    #twitter.update_status(status=tweet)
    photo = open("output.png","rb")
    twitter.update_status_with_media(status=tweet,media=photo)

if __name__=='__main__':
    run()
