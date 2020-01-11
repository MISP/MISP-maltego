# Install MISP-maltego remote transform as docker image.
#
# DO NOT USE THIS UNLESS YOU REALLY KNOW YOU NEED THIS
# - Most people usually probably want to use the local transforms 
# - Others the 'ATT&CK - MISP' form the Transform Hub 
#
# To build: "docker build MISP-maltego -t misp-maltego"
# To run: "docker run -p 8080:8080/tcp misp-maltego" if you want to run and enable portforwarding
# To stop: "docker ps" and "docker stop <instance_name>"
#
# Then configure your iTDS server 
# - to create all the transforms and seeds and point to your docker.
# - export the objects, icons and machines to a mtz and associate to the seed
#   Paired Configurations:
#   - in Maltego > Export Config, and select
#   -- Entities > MISP
#   -- Icons > MISP + intelligence icons
#   -- Machines
#   Save as "paired_config.mtz", upload on TDS


# TODO 
# - run the service with TLS, but that makes stuff more complex to automate

FROM python:3

RUN pip install PyMISP canari

# keep this for normal install
RUN pip install MISP-maltego

# use this for install from your own local git repo
# - first run "python setup.py sdist" to build the package
# - change the version number below
#COPY dist/MISP_maltego-1.4.1.tar.gz /usr/local/src/
#RUN pip install /usr/local/src/MISP_maltego-1.4.1.tar.gz

ENV LC_ALL='C.UTF-8'
ENV LANG='C.UTF-8'
ENV PLUME_ROOT='/var/plume'
RUN addgroup nobody
RUN canari install-plume --accept-defaults
RUN canari load-plume-package MISP_maltego --plume-dir /var/plume --accept-defaults

EXPOSE 8080/tcp

CMD ["/etc/init.d/plume", "start-docker"]