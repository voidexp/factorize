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

2. Setup and activate a Python virtual environment:

    `py -3 -m venv .venv`
    `. .venv\Scripts\Activate.ps1`

3. Install required dependencies:

    `pip install -r requirements.txt`

# Usage

Check out the inline help:

    python -m factorize --help


Print the required factories table for a 75 SPM and draw their connections graph
to a PNG file:

    > python -m factorize --factorio C:/Steam/steamapps/common/Factorio --draw science 75

    Loaded 198 recipes from C:\Steam\steamapps\common\Factorio
    IPM RECIPE                          CRAFTING MACHINE
    18 electric engine unit      ->    3 assembly machine 3
    20 flying robot frame        ->    6 assembly machine 3
    20 electric furnace          ->    2 assembly machine 3
    20 productivity module       ->    4 assembly machine 3
    30 piercing rounds magazine  ->    2 assembly machine 3
    30 grenade                   ->    4 assembly machine 3
    36 battery                   ->    3 chemical plant
    40 processing unit           ->    6 assembly machine 3
    40 firearm magazine          ->    1 assembly machine 3
    60 low density structure     ->   16 assembly machine 3
    60 stone wall                ->    1 assembly machine 3
    60 inserter                  ->    1 assembly machine 3
    60 transport belt            ->    1 assembly machine 3
    75 automation science pack   ->    5 assembly machine 3
    75 utility science pack      ->    7 assembly machine 3
    75 production science pack   ->    7 assembly machine 3
    75 chemical science pack     ->   12 assembly machine 3
    75 military science pack     ->    5 assembly machine 3
    75 logistic science pack     ->    6 assembly machine 3
    78 engine unit               ->   11 assembly machine 3
    132 pipe                      ->    1 assembly machine 3
    240 iron stick                ->    1 assembly machine 3
    270 lubricant                 ->    1 chemical plant
    362 advanced circuit          ->   29 assembly machine 3
    366 iron gear wheel           ->    3 assembly machine 3
    600 rail                      ->    2 assembly machine 3
    630 sulfur                    ->    6 chemical plant
    700 steel plate               ->   94 electric furnace
    840 stone brick               ->   23 electric furnace
    860 plastic bar               ->    8 chemical plant
    1080 sulfuric acid             ->    1 chemical plant
    1630 electronic circuit        ->   11 assembly machine 3
    4865 copper plate              ->  130 electric furnace
    5970 iron plate                ->  160 electric furnace
    6640 copper cable              ->   23 assembly machine 3

And you'll also have a nice plot of the factory structure saved in
_megafactory.png_.
