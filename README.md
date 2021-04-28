# Hercules: Tweet Retrieval and Machine Learning

This directory contains the software developed in the main
Machine Learning part of the project [Automated Analysis of
Online Behaviour on Social
Media](https://www.esciencecenter.nl/project/automated-analysis-of-online-behaviour-on-social-media),
a cooperation of the University of Groningen and the
Netherlands eScience Center. This project also has a
software repository regarding [finding
journalists](https://github.com/online-behaviour/find-journalists).

The software consist of a collection of Python scripts.
These can be divided in three groups:

1. tweet-fetching scripts
1. scripts related to the IEEE paper (Auckland)
1. scripts related to the Casablanca paper

There are also several unrelated scripts, which have been
left undocumented.

## Tweet-fetching scripts

### getTweetsUser.py

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

### getTweetText.py

The Python script getTweetText.py can be used for extracting
the tweets from the JSON output of getTweetsUser.py:

```
./getTweetText.py < getTweetsUser.py.out > file
```

## Scripts related to the IEEE paper (Auckland)

> Erik Tjong Kim Sang, Herbert Kruitbosch, Marcel Broersma and
> Marc Esteve del Valle, Determining the function of political
> tweets. In: Proceedings of the 13th IEEE International
> Conference on eScience (eScience 2017), IEEE, Auckland, New
> Zealand, 2017, pages 438-439, ISBN 978-1-5386-2686-3,
> doi:10.1109/eScience.2017.60. 
> ([PDF](https://ifarm.nl/erikt/papers/2017-escience.pdf),
> [bibtex](https://ifarm.nl/erikt/papers/2017-escience.txt)]

First, the data needs to be converted to the format required
by the machine learner [fasttext](https://github.com/facebookresearch/fastText).
We use tokenized text preceded by the class label, for 
example *__label__1 this is a tweet !*:

```
for FILE in test train
do
   ./expandReplies.py -t dutch-2012.$FILE.csv -r EMPTY |\
      cut -d' ' -f1,4- | sed 's/ RAWTEXT /*$/' > dutch-2012.$FILE.txt
done
```

Note that the data files with annotated tweets 
(dutch-2012.*) are unavailable.

Next, [fasttext](https://github.com/facebookresearch/fastText)
can be applied to the data:

```
fasttext supervised -input dutch-2012.train.txt -output MODEL \
   -dim 5 -minCount 300
fasttext predict MODEL.bin dutch-2012.test.txt |\
   paste -d ' ' - dutch-2012.test.txt | cut -d' ' -f1,2 |
      ./eval.py | head -1 | rev | sed 's/^ *//' | cut -d' ' -f1 | rev
```

For most of the experiments mentioned in Table II of the
paper, these two commands can be reused with a different
training file. Only the language modeling experiments
require an extra step, for creating the language models:

```
fasttext skipgram -input EXTRADATA -output VECTORS -dim 5 \
   -minCount 300
fasttext supervised -input dutch-2012.train.txt -output MODEL \
   -dim 5 -minCount 300 -pretrainedVectors VECTORS.vec
fasttext predict MODEL.bin dutch-2012.test.txt |\
   paste -d ' ' - dutch-2012.test.txt | cut -d' ' -f1,2 |\
   ./eval.py | head -1 | rev | sed 's/^ *//' | cut -d' ' -f1 | rev
```

We always remove the labels from the EXTRADATA files.

## Scripts related to the Casablanca paper

> Erik Tjong Kim Sang, Marc Esteve del Valle, Herbert Kruitbosch,
> and Marcel Broersma, Active Learning for Classifying Political 
> Tweets. In: Proceedings of the International Conference on
> Natural Language, Signal and Speech Processing (ICNLSSP),
> Casablanca, Morocco, 2017.

The experiments related to Figure 1 and Table 1 of the
paper, were performed with the bash script `run.sh`.

After annotating a file for active learning, the next data
file was generated with the bash script `run-make-batch`.

## Contact

Erik Tjong Kim Sang, e.tjongkimsang(at)esciencecenter.nl

# Information added by the python template

## Badges

| fair-software.eu recommendations | |
| :-- | :--  |
| (1/5) code repository              | [![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/online-behaviour/machine-learning) |
| (2/5) license                      | [![github license badge](https://img.shields.io/github/license/online-behaviour/machine-learning)](https://github.com/online-behaviour/machine-learning) |
| (3/5) community registry           | [![Research Software Directory](https://img.shields.io/badge/rsd-Research%20Software%20Directory-00a3e3.svg)](https://www.research-software.nl/software/online-behaviour-machine-learning) |
| (4/5) citation                     | [![DOI](https://zenodo.org/badge/87834727.svg)](https://zenodo.org/badge/latestdoi/87834727) |
| (5/5) checklist                    | [![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4837/badge)](https://bestpractices.coreinfrastructure.org/projects/4837) |
| howfairis                            | [![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F-green)](https://fair-software.eu) |
| **Other best practices**           | &nbsp; |
| Static analysis              | [![workflow scq badge](https://sonarcloud.io/api/project_badges/measure?project=online-behaviour_machine-learning&metric=alert_status)](https://sonarcloud.io/dashboard?id=online-behaviour_machine-learning) |
| Coverage              | [![workflow scc badge](https://sonarcloud.io/api/project_badges/measure?project=online-behaviour_machine-learning&metric=coverage)](https://sonarcloud.io/dashboard?id=online-behaviour_machine-learning) |
| **GitHub Actions**                 | &nbsp; |
| Build                              | [![build](https://github.com/online-behaviour/machine-learning/actions/workflows/build.yml/badge.svg)](https://github.com/online-behaviour/machine-learning/actions/workflows/build.yml) |
|  Metadata consistency              | [![cffconvert](https://github.com/online-behaviour/machine-learning/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/online-behaviour/machine-learning/actions/workflows/cffconvert.yml) |
| Lint                               | [![lint](https://github.com/online-behaviour/machine-learning/actions/workflows/lint.yml/badge.svg)](https://github.com/online-behaviour/machine-learning/actions/workflows/lint.yml) |
| Publish                            | [![publish](https://github.com/online-behaviour/machine-learning/actions/workflows/publish.yml/badge.svg)](https://github.com/online-behaviour/machine-learning/actions/workflows/publish.yml) |
| SonarCloud                         | [![sonarcloud](https://github.com/online-behaviour/machine-learning/actions/workflows/sonarcloud.yml/badge.svg)](https://github.com/online-behaviour/machine-learning/actions/workflows/sonarcloud.yml) |
| MarkDown link checker              | [![markdown-link-check](https://github.com/online-behaviour/machine-learning/actions/workflows/markdown-link-check.yml/badge.svg)](https://github.com/online-behaviour/machine-learning/actions/workflows/markdown-link-check.yml) |

## How to use machine_learning



The project setup is documented in [project_setup.md](project_setup.md). Feel free to remove this document (and/or the link to this document) if you don't need it.

## Installation

To install machine_learning from GitHub repository, do:

```console
git clone https://github.com/online-behaviour/machine-learning.git
cd machine-learning
python3 -m pip install .
```

## Documentation

Include a link to your project's full documentation here.

## Contributing

If you want to contribute to the development of machine-learning,
have a look at the [contribution guidelines](CONTRIBUTING.md).

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
