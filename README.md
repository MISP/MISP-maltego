# Quick start guide
This is a Maltego MISP integration tool allowing you to view (read-only) data from a MISP instance. 

Currently supported MISP elements are : Event, Attribute, Object, Tag, Taxonomy, Galaxy and relations.

Once installed you can start by creating a `MISPEvent` entity, then load the transform `EventToAttributes`.

Alternatively initiate a transform on an existing Maltego entity.
The currently supported entities are: `AS`, `DNSName`, `Domain`, `EmailAddress`, `File`, `Hash`, `IPv4Address`, `NSRecord`, `Person`, `PhoneNumber`, `URL`, `Website`


Dependencies:
* [PyMISP](https://github.com/MISP/PyMISP)
* [Canari3](https://github.com/redcanari/canari3)

## Installation:
```
git clone http://github.com/MISP/MISP-maltego
cd MISP-maltego
cp  src/MISP_maltego/resources/etc/MISP_maltego.conf MISP_maltego.conf
python3 setup.py install --user && canari create-profile MISP_maltego
```
Import the profile/transforms `MISP_maltego.mtz` in Maltego.  (Import|Export > Import Config)

Edit `$HOME/.canari/MISP_maltego.conf` and enter your `misp_url` and `misp_key`
```
[MISP_maltego.local]
misp_url = https://a.b.c.d
misp_key = verysecretkey
misp_verify = True
misp_debug = False
``` 
## Screenshot
![Screenshot](https://github.com/MISP/MISP-maltego/blob/master/doc/screenshot.png)

## License
This software is licensed under [GNU Affero General Public License version 3](http://www.gnu.org/licenses/agpl-3.0.html)

* Copyright (C) 2018 Christophe Vandeplas

Note: Before being rewritten from scratch this project was maintained by Emmanuel Bouillon. The code is available in the `v1` branch.


<hr />
The Canari welcome message:
# README - MISP_maltego

Welcome to Canari. You might be wondering what all these files are about. Before you can use the power of
`canari create-profile` you needed to create a transform package and that's exactly what you did here! I've given you a
directory structure to use in the following manner:

* `src/MISP_maltego` directory is where all your stuff goes in terms of auxiliary modules that you may need for 
  your modules
* `src/MISP_maltego/transforms` directory is where all your transform modules should be placed. An example
  `helloworld` transform is there for your viewing pleasure.
* `src/MISP_maltego/transforms/common` directory is where you can put some common code for your transforms like
  result parsing, entities, etc.
* `src/MISP_maltego/transforms/common/entities.py` is where you define your custom entities. Take a look at the
  examples provided if you want to play around with custom entities.
* `maltego/` is where you can store your Maltego entity exports.
* `src/MISP_maltego/resources/maltego` directory is where your `entities.mtz` and `*.machine` files can be
  stored for auto install and uninstall.
* `src/MISP_maltego/resources/external` directory is where you can place non-Python transforms written in other
  languages.

If you're going to add a new transform in the transforms directory, remember to update the `__all__` variable in
`src/MISP_maltego/transforms/__init__.py`. Otherwise, `canari install-package` won't attempt to install the
transform. Alternatively, `canari create-transform <transform name>` can be used within the
`src/MISP_maltego/transforms` directory to generate a transform module and have it automatically added to the
`__init__.py` file, like so:

```bash
$ canari create-transform foo
```

To test your transform, simply `cd` into the src directory and run `canari debug-transform`, like so:

```bash
$ canari debug-transform MISP_maltego.transforms.helloworld.HelloWorld Phil
%50
D:This was pointless!
%100
`- MaltegoTransformResponseMessage:
  `- Entities:
    `- Entity:  {'Type': 'test.MyTestEntity'}
      `- Value: Hello Phil!
      `- Weight: 1
      `- AdditionalFields:
        `- Field: 2 {'DisplayName': 'Field 1', 'Name': 'test.field1', 'MatchingRule': 'strict'}
        `- Field: test {'DisplayName': 'Field N', 'Name': 'test.fieldN', 'MatchingRule': 'strict'}
```

Cool right? If you have any further questions don't hesitate to drop us a line;)

Have fun!
