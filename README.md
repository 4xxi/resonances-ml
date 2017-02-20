* Master: [![Build Status](https://travis-ci.org/4xxi/resonances-ml.svg?branch=master)](https://travis-ci.org/4xxi/resonances)
* Develop: [![Build Status](https://travis-ci.org/4xxi/resonances-ml.svg?branch=develop)](https://travis-ci.org/4xxi/resonances)

# Resonances ML

## Abstract

The application identifies three-body resonances using machine learning (ML)
techniques. It uses data from AstDys catalog as source of feature
dataset and it uses text file contains resonanct asteroids, the file will be used for
forming target vector. The application allows to check desired ML technique for
common metrics and for influence of pointed features.
The application by default has:

* Catalogs.
* Lists of 50, 100, 200 resonant asteroids for Jupiter Saturn resonance with integers 4 -2 -1.
* Lists of 50, 100, 200 resonant asteroids for Jupiter Saturn pure resonance with integers 4 -2 -1.
* List of all resonant asteroids for Jupiter Saturn resonance with integers 4 -2 -1.
* List of all resonant asteroids for Jupiter Saturn pure resonance with integers 4 -2 -1.
* Configuration file with couple of ML techniques suitable for classifying.
  Suitability of them determined by related research.

## Installation

You can install the Resonances ML using Python package manager pip

`pip install git+https://github.com/4xxi/resonances`

## Usage

First of all huge part of input data is in configuration. Configuration data is
stored by YAML format.  You can customize it by pointing your configuration
file.  Do `python -m resonanceml dump-config` to get default configuration. You
can redirect output to your file.  Let's say you want to make configuration
file `my-config.yml`. For this execute `python -m resonanceml dump-config >
my-config.yml` When you get your own configuration file you can customize it by
you favorite text editor and you are able for pointing it for the application.
Make `python -m resonanceml -c  my-config.yml <another command of the
application>` for executing some another command of the application based on
your configuration file.

Also every command has option `--help`. If some of commands or options is not clear checkout `python -m resonancesml --help` or
`python -m resonancesml <some_command> --help`

### Choosing classifier

Use command `python -m resonancesml choose-clf` to compare classifiers' scores.
This command uses classifiers from section `classifiers_for_comparing` in
configuration (see `python -m resonancesml dump-config`).
Example: `python -m resonancesml choose-clf -l input/librations/first50_librated_asteroids_4_-2_-1 -c syn`.

### Inflence fields

For comparing significance of fields from catalog there is command `python -m
resonancesml influence-fields`. It iterate searches cases of indieces
combinations from configuration section `influence`.

### Classification by all asteroids

Commands `choose-clf`, `influence-fields`, `classify-all`, `get_optimal_parameters`.

### Getting resonant asteroids

Command: `python -m resonancesml get -n 2000 -c syn -e '2' --clf='KNN 0'`.

This will returns resonant asteroids classified by ML technique K Nearest
Neighbors (KNN) using first (0) argument preset. Count is from 0. Point
`--clf='DT 1'` to use Decision Tree with second (1) argument preset.

Length of learning dataset is equal to 2000. If length is not pointed, learning
set will contain asteroids from 1 to last known resonant asteroid.

Features are got from catalog of synthetic (**syn**) elements. Catalog is got from
`input` directory inside project directory. You can use custom catalog pointing in configuration file.

Option `-e '2'` means that only third field will be used from feature set.
Count is from 0. Point `-e='2 4'` to use third and fifth fields. Indices can be
negative it means that count will from **last column**. Option `-e='2 -1'` means to
use third and last column. Note one more thing. Before classifying the
application builds cache that contains additional features it means that number
of available columns is not equal to number of columns from catalog. Also note
that **catalogs has difference between positions of features**. For example catalog
of orbital elements contains magnitude values in second column but catalog of
synthetic elements has semi-major axis in second column.

More details are available by command `python -m resonancesml get --help`

#### Custom configuration file

You can point your own configuration file in YAML format. Add option '-c' to get this.
`python -m resonancesml -c /path/to/my/config.yaml get -n 2000 -c syn -e '2' --clf='KNN 0'`

Execute command `python -m resonancesml dump-config` to see default configuration file.

### Test classifier

Command: `python -m resonancesml test-clf -n 2000 -c syn -e '2' --clf='KNN 0' -r`.
Description of the options [above](#getting-resonant-asteroids)

More details are available by command `python -m resonancesml test-clf --help`

### Get influence of fields

Command `python -m resonancesml influence-fields -c syn --clf='DT 0'`. Meaning
of this options is same as in [above](#getting-resonant-asteroids) but this command
also has one different option `-l /path/to/list`. This path to list of resonant asteroids.

### Plotting

Command: `python -m resonancesml plot -n 2000 -c syn`. Meaning
of this options is same as in [above](#getting-resonant-asteroids)

More details are available by command `python -m resonancesml plot --help`
