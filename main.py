#Import Libraries
import string
import aiml
import pandas as pd
import sys
from nltk.sem import Expression
from nltk.inference import ResolutionProver
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
read_expr = Expression.fromstring
import enchant
d = enchant.Dict("en_GB")
from tmdbv3api import TMDb
from tmdbv3api import Movie
import time
time.clock = time.process_time
import numpy
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import tkinter
from tkinter import filedialog

#  Initialise AIML
kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles="mybot-basic.xml")

#  Aquire and Check KB
kb=[]
data = pd.read_csv('kb.csv', header=None)
[kb.append(read_expr(row)) for row in data[0]]

df = pd.read_csv('qs.csv',encoding='cp1252', names = ['r1', 'r2'])
x=df.r1
y=df.r2

# Validate Knowledge Base
def Validate(kb):
    Check = "xxx is yyy"
    object,sub=Check.split(' is ')
    sub = sub.replace (" ", "")
    expr=read_expr(sub + '(' + object + ')')
    answer=ResolutionProver().prove(expr, kb)
    print ("File is being checked")
    if answer:
        print('Error found.')
        sys.exit()
Validate(kb)

# Search The Movie Database
def search_movie(user_inp):
    movie = Movie()
    tmdb = TMDb()
    #sets API key
    tmdb.api_key = 'c89eeed718bce0da28081f264650efd1'
    tmdb.language = 'en'
    tmdb.debug = True
    #searches the movie database with user input
    search = movie.search(user_inp)
    for res in search:
            #Prints the movie title
            print('You made a search regarding: ' + res.title)
            #Prints the movie release date
            print('\n' + res.title + ' was released in: ' + res.release_date)
            #Prints the movie rating
            if res.vote_average > 5:
                print('\nIMDB gave it a strong rating of: ', res.vote_average)
            else:
                print('\nIMDB gave it a weak rating of:', res.vote_average)
            print('\nHere is a brief synopsis of the plot:\n\n' + res.overview)

            if res.title != Movie_Name:
                break

# I know Sequence
def i_know_that():
    #Cleans the object and subject statement
     object,subject=params[1].split(' is ')
     expr=read_expr(subject + '(' + object + ')')
     #Compares the input to the knowledge base, returns truw/false
     answer=ResolutionProver().prove(expr, kb, verbose=False)
     #Checks if answer matches
     if answer:
         print("That matches my records, nice job!")
     #Checks for similar matches and then suggests correct answers    
     else:
         if not(d.check(subject)):
             subject = d.suggest(subject)[0]
             print("I think you meant "+subject+"\n")
             expr=read_expr(subject + '(' + object + ')')
             answer = ResolutionProver().prove(expr, kb)
             if answer:
                print("Spot on, nice work!")
             if not(d.check(object)):
                object = d.suggest(object)[0]
                print("Did you mean "+object+"\n")

                expr=read_expr(subject + '(' + object + ')')
                answer = ResolutionProver().prove(expr, kb)
             if answer:
                print("That matches my records!")
     #Checks if the answer is false
     if answer !=True:
        NewExpr=read_expr("-" + subject + '(' + object + ')')
        NewAnswer=ResolutionProver().prove(NewExpr, kb, verbose=False)
        if NewAnswer:
            print("This goes against what I know to be true!")
        #|If there is no value similar in the knowledge base then this will update the KB with the provided values
        else:
            print("Sorry I do not have an answer for this")
            kb.append(expr)
            print(str(expr))
            updatedkb = open("kb.csv", "a")
            updatedkb.write("\n" + str(expr))
            updatedkb.close()
            print('I have updated my knowledge base that',object,'is', subject)

# Check that sequence
def check_that():
     #Cleans the object and subject statement
     object,subject=params[1].split(' is ')
     expr=read_expr('-' + subject + '(' + object + ')')
     #Compares the input to the knowledge base, returns true/false
     answer=ResolutionProver().prove( expr, kb, verbose=False)
     #Checks if its a match, true statement
     if answer:
        print("That matches my records, nice job!")
     #Checks for similar matches and makes suggestions to correct values
     else:
        if not(d.check(subject)):
            subject = d.suggest(subject)[0]
            print("I believe you meant: "+subject+"\n")
            expr_1=read_expr(subject + '(' + object + ')')
            answer = ResolutionProver().prove(expr_1, kb)
        if answer:
            print("Spot on, nice work!")

        if not(d.check(object)):
            object = d.suggest(object)[0]
            print("I believe you meant: "+object+"\n")

            expr_1=read_expr(subject + '(' + object + ')')
            answer = ResolutionProver().prove(expr_1, kb)
            if answer:
                print("This is a match with what I have in my records, nice job.")
     #Checks to see if false and informs the user
     if answer !=True:
         #Checks again to ensure it is false
         NewExpr=read_expr("-" + subject + '(' + object + ')')
         NewAnswer=ResolutionProver().prove(NewExpr, kb, verbose=False)
         if NewAnswer:
             print("Sorry this is not in my records\nKnow you can add this by saying 'I know that * is *")
         else:
             print("Sorry, against our records this is false.")
             
#Prints the full knowledge base
def print_all_known():
    print(*kb, sep = "\n")

# Cleans input

def clean_string(text):
    #Removes any punctuation from the sentence
    text = ''.join([word for word in text if word not in string.punctuation])
    #Returns all values in lowercase
    text = text.lower()
    return text

# Sets the vectors required for cosine
def cosine_sim_vectors(vec1, vec2):
    vec1 = vec1.reshape(1,-1)
    vec2 = vec2.reshape(1,-1)
    return cosine_similarity(vec1, vec2)[0][0]

# Finds the highest value
def get_highest_value(fs,userIndex):
    highest = 0
    highestIndex = 0
    #Loops throguh the saved values to find the highest cosine value
    for i in range(len(fs) -1):
        current = cosine_sim_vectors(vectors[userIndex], vectors[i])
        if current > highest:
            highest = current
            highestIndex = i
    return highest, highestIndex
#Calls the image classification
def image_classification():
    #Defines the class names (This is already done in the model it is to correctly assign the predicted values)
    class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
                   'dog', 'frog', 'horse', 'ship', 'truck']
    
    #Loads the saved model
    new_model = tf.keras.models.load_model("C:/Users/emers/OneDrive/Desktop/Courseworks/Artificial Intelligence/MovieChatbot/MovieChatbot/my_model.h5")
    #Prints the model summary uncomment if needed
    #new_model.summary()

    print("Please select an image from the file explorer that has been opened:")
    root = tkinter.Tk()
    #Opens a file explorer for the user to select an image
    img_path = filedialog.askopenfilename(parent=root, initialdir="/",
                                    title='Please select a directory')
    #Clears the root to unload the dialog box
    root.update()
    
    #Saves the selected image and resizes it to fit the model
    new_img = image.load_img(img_path, target_size=(32, 32,))
    x_trans = tf.transpose(new_img, perm=[ 0, 1, 2])
    x_expanded = np.expand_dims(x_trans, axis=0)
    #Makes a prediction with the model
    predictions_single = new_model.predict(x_expanded) 
    
    #Print the results
    print("What you saw in this movie was a: " + class_names[np.argmax(predictions_single[0])])




    


# Welcome the user
print("Hello! I am your personal guide for movies. Simply give me a film or a question for anything movie related.")
# Main loop


while True:
    #get user input
    try:
        userInput = input("> ")
    except (KeyboardInterrupt, EOFError) as e:
        print("Bye!")
        break
    #pre-process user input and determine response agent (if needed)
    responseAgent = 'aiml'
    #activate selected response agent
    if responseAgent == 'aiml':
        answer = kern.respond(userInput)
        print("\n")
    #post-process the answer for commands
    if answer[0] == '#':
        params = answer[1:].split('$')
        cmd = int(params[0])
        if cmd == 0:
            print(params[1])
        elif cmd == 1:
            #Movie API
            Movie_Name = params[1]
            try:
                search_movie(Movie_Name)
            except:
                print("My apologies,my records appear to be missing this one!")
        elif cmd == 2:
            #Calls the function to check the KB, and update according to the "I know" sequence
            i_know_that()

        elif cmd == 3: 
            #Calls the function to check the KB, and check data inputed against existing data
           check_that()
           
        elif cmd ==4:
            print_all_known()
            
        elif cmd ==5:
            image_classification()
        
        elif cmd == 98:
            print("Peace Out")
            break
        elif cmd == 99:
            fs=[]
            #sorts the questions from a csv into a list
            for i in range(len(x)): 
                fs.append(df._get_value(i,'r1'))

            fs.append(userInput)
            #Sorts the answers from a csv into a list
            listResponse2=[]
            for i in range(len(y)):
                listResponse2.append(df._get_value(i,'r2')) 
            userIndex= len(fs) -1
            #Removes any punctuation within the sentences
            tidy_text = list(map(clean_string, fs))
            #Vectorising the list into an array
            vectorizer = CountVectorizer().fit_transform(tidy_text)
            vectors = vectorizer.toarray()
            #Set the Cosine Similarity
            csim = cosine_similarity(vectors)
            #Aquire the highest cosine index
            highest,highestIndex = get_highest_value(tidy_text,userIndex)
            #Save the best match into a variable
            listResponse3 = listResponse2[highestIndex]
            #Print the best match
            print(listResponse3)