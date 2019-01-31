# MISP-Maltego User Guide

This user guide should help you through the installation of **MISP-Maltego**, and should guide you how to use it through a few use-cases. As this is a collaborative project, do not hesitate to propose changes, write other use-cases or raise [feature requests](https://github.com/MISP/MISP-maltego/issues) for missing features.

## Installation
These instructions have been tested on Ubuntu 18.04 LTS, but should be similar on other systems.
1. Download and install [Maltego](https://www.paterva.com/web7/downloads.php)
2. Install dependencies:  `sudo apt install git build-essential python3-setuptools python3-dev python3-pip`
3. Clone the repository, install and create the Maltego local transform bundle.
   To the question *".canari/canari.conf already exists, would you like to overwrite it?"* you will probably want to answer yes.
```
git clone https://github.com/MISP/MISP-maltego.git
cd MISP-maltego
sudo pip3 install .
canari create-profile MISP_maltego
```
5. Import this bundle in Maltego. 
   1. Open Maltego
   2. Click on the home button (Maltego icon, top-left corner).
   3. Click on 'Import'
   4. Click on 'Import Configuration'.
   5. Load the `MISP_maltego.mtz` file and follow the prompts.
6. Edit `$HOME/.canari/MISP_maltego.conf` and enter your `misp_url` and `misp_key`

## Custom Entities
MISP-Maltego tries to use as much as possible the default Paterva entities, or the most popular from the community. It however comes with a few custom entities: 
* **MISPEvent**: A representation of an *Event* on MISP, containing *Attributes* (MISP) / *Entities* (Maltego)
* **MISPObject**: A way to group associated attributes in a structured way.
* **MISPGalaxy**: A *Tag* containing much more metadata. Please refer to the [MISP Galaxy
](https://github.com/MISP/misp-galaxy) for more information. **MITRE ATT&CK** is for example completely available through MISPGalaxy entities (see use-cases for an example)

# Use Cases
## Transform on existing data
TODO
## Transform from MISP Event ID
TODO
## Transform from Galaxy
TODO
## Visualise MITRE ATT&CK
TODO