

![logo](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/logo.png)

This is a [Maltego](https://www.paterva.com/web7/) [MISP](https://www.misp-project.org) integration tool allowing you to view (read-only) data from a MISP instance. 
It also allows browsing through the [MITRE ATT&CK](https://attack.mitre.org/) entities. (no MISP connection needed)

This user guide should help you through the [installation](#installation) of **MISP-Maltego**, and should guide you how to use it through a few [use-cases](#use-cases). As this is a collaborative project, do not hesitate to propose changes, write other use-cases or raise [feature requests](https://github.com/MISP/MISP-maltego/issues) for missing features.

## Quick start
Currently supported MISP elements are : Event, Attribute, Object (incl relations), Tag, Taxonomy, Galaxy (incl relations).

Once installed you can start by creating a `MISPEvent` entity, then load the Machine `EventToAll` or the transform `EventToAttributes`.

Alternatively initiate a transform on an existing Maltego entity.
The currently supported entities are: `AS`, `DNSName`, `Domain`, `EmailAddress`, `File`, `Hash`, `IPv4Address`, `NSRecord`, `Person`, `PhoneNumber`, `URL`, `Website`

For MITRE ATT&CK pivoting, feel free to start with an `Attack Technique`, `Software`, `Threat Actor`, or `MISPGalaxy`. Create your entity, enter a keyword such as `%gama%` and use the `Search in MISP` transform to get started. 

## Installation
### Transform Hub
Open the Transform Hub, locate **ATT&CK - MISP** and press the **Install** button. 

Your transforms will go through Paterva's servers and ours. See the [Transform Hub Disclaimer](https://github.com/MISP/MISP-maltego/blob/master/TRANSFORM_HUB_DISCLAIMER.md) for more information.

- ATT&CK transforms do not require a MISP server or API key to be configured.
- MISP transforms requires your MISP server to be reachable from the internet! To enter your MISP server URL and key click **Details** on the Transform Hub item and then **Settings** at the bottom right. 

### Local Transform Installation
If you trust nobody, or just want to connect to your local MISP server you can install everything as local transforms.

These instructions have been tested on Ubuntu 18.04 LTS, but should be similar on other systems.
1. Download and install [Maltego](https://www.paterva.com/web7/downloads.php)
2. Install using pip: `sudo pip3 install MISP-maltego`
3. Generate the Maltego bundle: `canari create-profile MISP_maltego`
4. Import this bundle in Maltego. 
   1. Open Maltego
   2. Click on the home button (Maltego icon, top-left corner).
   3. Click on 'Import'
   4. Click on 'Import Configuration'.
   5. Load the `MISP_maltego.mtz` file and follow the prompts.
5. Edit `$HOME/.canari/MISP_maltego.conf` and enter your `misp_url` and `misp_key`

## Custom Entities
MISP-Maltego tries to use as much as possible the default Paterva entities, or the most popular from the community. It however comes with a few custom entities: 
* **MISPEvent**: A representation of an *Event* on MISP, containing *Attributes* (MISP) / *Entities* (Maltego)
* **MISPObject**: A way to group associated attributes in a structured way.
* **MISPGalaxy**: A *Tag* containing much more metadata. Please refer to the [MISP Galaxy](https://github.com/MISP/misp-galaxy) for more information. **MITRE ATT&CK** is for example completely available through MISPGalaxy entities (see use-cases for an example)
* **Attack Technique**: Attack patterns or techniques, see [MITRE ATT&CK](https://attack.mitre.org/techniques/enterprise/) for more information.
* **Threat Actor**: Threat actor or intrusion sets.
* **Software**: Software is a generic term for custom or commercial code, operating system utilities, open-source software, or other tools used to conduct behavior modeled in ATT&CK. 

# Use Cases
## Transform on existing data
In this use case we will be using already existing entities and will initiate a transform using MISP. The currently supported entities are: `AS`, `DNSName`, `Domain`, `EmailAddress`, `File`, `Hash`, `IPv4Address`, `NSRecord`, `Person`, `PhoneNumber`, `URL`, `Website`.

Example:
* create an entity `domain` with the value `1dnscontrol.com`.
* right click and choose *Local Transforms*  > *MISP_maltego* > *Domain To Event*  
![animated screenshot](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/usecase1-transform.gif)
* continue loading transforms on the *MISP Event*

## Transform from MISP Event ID
While MISP already has a graphing capability we would like to use the power of Maltego to look at the data and expand the work.
* Create a *MISP Event* and give it an `event id`, or `UUID`
* One **manual** way is to right click and choose *Local Transforms* > *MISP_maltego* > *Event To Attributes* 
  * Notice the event is transformed to *Attributes*, *Objects*, *Tags*, *Galaxies* and related *MISP Events*
  * You can now further transform on an *Object* > *Object To Attributes* and see the content of the object
![machine transforms](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/usecase2-manual.gif)
* Alternatively you can also use the **Maltego Machine** to speed up things. 
   * Click on the *MISP Event* and in the left menu choose *Event to All* in the *Machines* section. 
![machine transforms](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/usecase2-machine-menu.png)
   * Notice that the whole event, objects and such will get expanded with data from your MISP instance.
![animated screenshot](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/usecase2-machine.gif)
* You can now further transform on any data.

## Which data is already in MISP?
If you use MISP as central database it can be quite convenient to know which data is present in MISP, and which data is not; especially after using a number of other transforms.
To permit this MISP-Maltego will always add a green bookmark to all the data that is present in MISP.
![green bookmark](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/usecase3-bookmark.png)


## Searching in MISP using keywords
As with the MISP attribute search through the MISP Web UI you can use `%` wildcards at the front and end to specify the substring. You might be tempted to always use `%keyword%`, but bare in mind how databases indexes work; a search for `keyword%` will always be much faster than `%keyword`.
![Search in MISP](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/search_in_misp.gif)


## Transform from Galaxy
Galaxies are actually tags with much more contextual data. Examples are threat actors, malware families, but also the whole MITRE ATT&CK data is available as Galaxy. All this data comes from the [MISP Galaxy](https://github.com/MISP/misp-galaxy) repository. Today the integration is not done using a MISP server because of limitations in MISP.
You might encounter Galaxies when transforming from MISP Events or Attributes. An alternative use-case is by starting immediately from a Galaxy.
There are 3 ways to manually create a good Galaxy Entity.
1. Using a find capability (see below)
2. Create the Galaxy and set the UUID. You can find the UUIDs in the [MISP Galaxy](https://github.com/MISP/misp-galaxy) repository.
3. Create the Galaxy with the right tag name; for example: `misp-galaxy:`

To use the magical search feature:
* Create a *MISP Galaxy* and type the keyword as value.
* Run the *Galaxy To Relation* transform, notice the search results will appear as connected entities
* Remove the non-relevant entities, including the your search-keyword
![animated galaxy search](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/usecase4-galaxy-search.gif)

## Visualize MITRE ATT&CK
Apply the same steps for MITRE ATT&CK browsing:

![animated ATTACK](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/usecase5-attack.gif)

You might end up with such a graph:

![ATTACK](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/usecase5-attack.png)

## Visualise common ATT&CK patterns
Having access to a large amount of Threat information through MISP Threat Sharing communities gives you outstanding opportunities to aggregate this information and take the process of trying to understand how all this data fits together telling a broader story to the next level. We are transforming technical data or indicators of compromise (IOCs) into cyber threat intelligence. This is where the analytical challenge begins. [[read more](https://www.misp-project.org/2019/10/27/visualising_common_patterns_attack.html)]


## Massively large MISP event? Think before you transform.
In some communities such as the [COVID-19 MISP](https://www.misp-project.org/covid-19-misp/) some events contain tens of thousands attributes. Loading all the attributes from these events might not be a good idea if you do not have Maltego XL.
You can see the amount of attributes and objects in the Event properties, so you can think before you click:

![object count](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/event_count_attr1.png)![attribute count](https://raw.githubusercontent.com/MISP/MISP-maltego/master/doc/img/event_count_attr2.png)






## License
This software is licensed under [GNU Affero General Public License version 3](http://www.gnu.org/licenses/agpl-3.0.html)

* Copyright (C) 2018 Christophe Vandeplas

Note: Before being rewritten from scratch this project was maintained by Emmanuel Bouillon. The code is available in the `v1` branch.

The logo is CC-BY-SA and was designed by Françoise Penninckx

The icons in the intelligence-icons folder are from [intelligence-icons](https://github.com/MISP/intelligence-icons) licensed CC-BY-SA - Françoise Penninckx, Brett Jordan
