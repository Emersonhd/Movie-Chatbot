To preview the bulk of the code direct your attention to main.py

KB is a knowledge base for the chatbot.

my_model.h5 is the logic for that chatbot using a knn algorithm to match question posed to the chatbot with the nearest answer it has available out of a set of options examples can be seen in qs.csv.

mybot-basic.xml is the different choice of answers the model has available, this will cause either filler conversation, one of two API calls. interaction with the kb, or a call for image classifcation which was a feature I was testing towards the end, at the final update it was able to accurately identify basic animal types seen on a small set of images.



