# MISP Maltego Remote Transform Disclaimer
**When using the MISP Maltego transforms using the Transform Hub (not the locally installed version) you need to know you are are sending data, including your MISP URL and API key to 3rd parties.**

The public Transform Distribution Server (TDS) is located on the Internet and is free for all to use. It’s a convenient way to immediately start writing remote transforms. Since this server is located on Paterva’s infrastructure data (entity, and settings) will be flowing from the Maltego GUI to this server. Paterva states they DO NOT store the details of your transforms (entities, MISP URL, API KEY).

Finally it will flow further to a server managed by the MISP-maltego developer(s), where the transform code runs. We also DO NOT store or look at the details of your transforms (entities, MISP URL, API KEY). As you can see in the code (open source), this data is only used live in memory to provide the transform functionality. The only reasons why we would be seeing this data is by accident; while troubleshooting or by unintentional mis-configuration.

We do keep standard HTTP logs for troubleshooting and anonymous statistics, although these contain the IP addresses of Paterva's TDS server, and not yours.

**DO NOT use these Transform Hub transforms if you do not agree or if this is in violation with your MISP community.**

**If so, feel free to use the MISP-Maltego transforms locally, where all the code runs on your own system. Installation instructions can be found [here](https://github.com/MISP/MISP-maltego/blob/master/doc/README.md#installation).**

You can also run this on your own iTDS server if you have the license. Have a look at the [Dockerfile](https://github.com/MISP/MISP-maltego/blob/master/Dockerfile) for more info.


## More info
For more information please read Paterva's and Canari's documentation:
* [http://www.canariproject.com/en/latest/canari.quickstart.html#making-transforms-remote](http://www.canariproject.com/en/latest/canari.quickstart.html#making-transforms-remote)
* [https://docs.maltego.com/support/solutions/articles/15000020198-what-is-itds-](https://docs.maltego.com/support/solutions/articles/15000020198-what-is-itds-)
* [https://www.paterva.com/buy/maltego-servers.php](https://www.paterva.com/buy/maltego-servers.php)
