# Machine Learning in project Online Behaviour

This directory contains the software developed in the main
Machine Learning part of the project [Automated Analysis of
Online Behaviour on Social
Media](https://www.esciencecenter.nl/project/automated-analysis-of-online-behaviour-on-social-media),
a cooperation of the University of Groningen and the
Netherlands eScience Center. This project also has a
software repository regarding [finding
journalists](https://github.com/online-behaviour/find-journalists)

## getTweetsUser.py

The Python script getTweetsUser.py can be used for obtaining
tweets from certain users. Run like:

```
./getTweetsUser.py barackobama realdonaldtrump > file
```

It will retrieve all available tweets from the specified
users and store these in the specified file. The tweets are
stored in the data format
[JSON](https://en.wikipedia.org/wiki/JSON). The command may
require several minutes to complete. 

The script needs two things to run:

First: you will need to install the Twitter package from:
[https://github.com/sixohsix/twitter](https://github.com/sixohsix/twitter)
The commands for this on Linux and MacOSX are:

```
git clone https://github.com/sixohsix/twitter
cd twitter
python setup.py build
sudo python setup.py install
```

Second: you need to store your Twitter account data in a file named
"definitions.py" in the same directory as getTweetsUser.py. The file
should contain the following lines:

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

