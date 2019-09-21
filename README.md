Factorize
=========

A set of utility scripts for Factorio players that allow to:

* Compute the factory configuration for producing given recipes at desired rates.
* Compute the factory configuration for desired Science-Per-Minute production rate.
* Draw the graph of the factory configuration to a PNG file.

# Setup
The steps below are provided, assuming to be executed on a Windows machine with
Python 3.7+ installed.

Check out Google or http://python.org to see how to install Python.

All the commands are to be executed in PowerShell.

OSX/Linux users are expected to know how to setup and run the script by themeselves.

1. Clone this repository:

    `git clone git@github.com:V0idExp/factorize.git`
    `cd factorize`

2. Setup and activate a Python 3 virtual env:

    `py -3 -m venv .env`
    `.env\Scripts\Activate.ps1`

3. Install required dependencies:

    `pip install -r factorize\requirements.txt`

# Usage

Check out the inline help:

    python factorize\factorize.py --help


Compute the number of factories for a 75 SPM and draw their configuration to a
PNG file:

    python factorize\factorize.py --draw science 75
