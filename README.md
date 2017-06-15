# Machine Learning in project Online Behaviour

This directory contains the software developed in the main
Machine Learning part of the project [Automated Analysis of
Online Behaviour on Social
Media](https://www.esciencecenter.nl/project/automated-analysis-of-online-behaviour-on-social-media),
a cooperation of the University of Groningen and the
Netherlands eScience Center. This project also has a
software repository regarding [finding
journalists](../find-journalists)

## getTweetsUser.py

The Python script getTweetsUser.py can be used for obtaining
tweets from certain users. Run like:

```
./getTweetsUser.py barackobama realdonaldtrump > file
```

It will retrieve all available tweets from the specified
used and store these in the specified file. The command may
require several minutes to complete. 

The script needs your Twitter account data to be stored in a
file definitions.py in the format:

```
# twitter.com authentication keys
token = "???"
token_secret = "???"
consumer_key = "???"
consumer_secret = "???"
```

Replace the strings "???" with the key information from 
https://apps.twitter.com , see
https://www.slickremix.com/docs/how-to-get-api-keys-and-tokens-for-twitter/
for instructions

## getTweetText.py

The Python script getTweetText.py can be used for extracting
the tweets from the JSON output of getTweetsUser.py:

```
./getTweetText.py < getTweetsUser.py.out > file
```

## (other scripts need to be documented ...)

## Contact

Erik Tjong Kim Sang, e.tjongkimsang(at)esciencecenter.nl

