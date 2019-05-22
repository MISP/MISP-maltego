# Quick start guide
This is a [Maltego](https://www.paterva.com/web7/) [MISP](https://www.misp-project.org) integration tool allowing you to view (read-only) data from a MISP instance. 

It also allows browsing through the [MITRE ATT&CK](https://attack.mitre.org/) entities.

Currently supported MISP elements are : Event, Attribute, Object (incl relations), Tag, Taxonomy, Galaxy (incl relations).

Once installed you can start by creating a `MISPEvent` entity, then load the Machine `EventToAll` or the transform `EventToAttributes`.

Alternatively initiate a transform on an existing Maltego entity.
The currently supported entities are: `AS`, `DNSName`, `Domain`, `EmailAddress`, `File`, `Hash`, `IPv4Address`, `NSRecord`, `Person`, `PhoneNumber`, `URL`, `Website`


## Installation and User Guide:
Installation is fairly easy by using `pip`, just read the steps in the [documentation](https://github.com/MISP/MISP-maltego/blob/master/doc/README.md).

The [User Guide](https://github.com/MISP/MISP-maltego/blob/master/doc/README.md#use-cases) gives some example use-cases.


## Screenshot
![Screenshot](https://github.com/MISP/MISP-maltego/blob/master/doc/screenshot.png)

![ATT&CK](https://github.com/MISP/MISP-maltego/blob/master/doc/attack.jpg)


## License
This software is licensed under [GNU Affero General Public License version 3](http://www.gnu.org/licenses/agpl-3.0.html)

* Copyright (C) 2018 Christophe Vandeplas

Note: Before being rewritten from scratch this project was maintained by Emmanuel Bouillon. The code is available in the `v1` branch.

The icons in the intelligence-icons folder are from [intelligence-icons](https://github.com/MISP/intelligence-icons) licensed CC-BY-SA - Françoise Penninckx, Brett Jordan
