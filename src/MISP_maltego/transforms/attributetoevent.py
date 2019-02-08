from canari.maltego.entities import Hash, Domain, IPv4Address, URL, DNSName, AS, Website, NSRecord, PhoneNumber, EmailAddress, File, Hashtag, Company, Alias, Twitter
from canari.maltego.transform import Transform
from canari.maltego.message import Bookmark
# from canari.framework import EnableDebugWindow
from MISP_maltego.transforms.common.util import get_misp_connection, event_to_entity

__author__ = 'Christophe Vandeplas'
__copyright__ = 'Copyright 2018, MISP_maltego Project'
__credits__ = []

__license__ = 'AGPLv3'
__version__ = '0.1'
__maintainer__ = 'Christophe Vandeplas'
__email__ = 'christophe@vandeplas.com'
__status__ = 'Development'


# @EnableDebugWindow
class AttributeInMISP(Transform):
    """This method puts a green bookmark on each of the Entities that are present in the MISP database"""
    display_name = 'in MISP?'
    input_type = None

    def do_transform(self, request, response, config):
        maltego_misp_attribute = request.entity
        misp = get_misp_connection(config)
        events_json = misp.search(controller='events', values=maltego_misp_attribute.value, withAttachments=False)
        in_misp = False
        for e in events_json['response']:
            in_misp = True
            break
        if in_misp:
            request.entity.bookmark = Bookmark.Green
            response += request.entity
        return response


# @EnableDebugWindow
class AttributeToEvent(Transform):
    # The transform input entity type.
    input_type = None

    def do_transform(self, request, response, config):
        maltego_misp_attribute = request.entity
        misp = get_misp_connection(config)
        events_json = misp.search(controller='events', values=maltego_misp_attribute.value, withAttachments=False)
        in_misp = False
        for e in events_json['response']:
            in_misp = True
            response += event_to_entity(e)
        if in_misp:
            request.entity.bookmark = Bookmark.Green
            response += request.entity
        return response

    def on_terminate(self):
        """This method gets called when transform execution is prematurely terminated. It is only applicable for local
        transforms. It can be excluded if you don't need it."""
        pass


class HashToEvent(AttributeToEvent):
    input_type = Hash


class DomainToEvent(AttributeToEvent):
    input_type = Domain


class IPv4AddressToEvent(AttributeToEvent):
    display_name = 'IPv4Address To Event'
    input_type = IPv4Address


class URLToEvent(AttributeToEvent):
    display_name = 'URL To Event'
    input_type = URL


class DNSNameToEvent(AttributeToEvent):
    display_name = 'DNSName To Event'
    input_type = DNSName


class ASToEvent(AttributeToEvent):
    display_name = 'AS To Event'
    input_type = AS


class WebsiteToEvent(AttributeToEvent):
    input_type = Website


class NSRecordToEvent(AttributeToEvent):
    display_name = 'NSRecord To Event'
    input_type = NSRecord


class PhoneNumberToEvent(AttributeToEvent):
    input_type = PhoneNumber


class EmailAddressToEvent(AttributeToEvent):
    input_type = EmailAddress


class FileToEvent(AttributeToEvent):
    input_type = File


class HashtagToEvent(AttributeToEvent):
    input_type = Hashtag


class AliasToEvent(AttributeToEvent):
    input_type = Alias


class TwitterToEvent(AttributeToEvent):
    input_type = Twitter


class CompanyToEvent(AttributeToEvent):
    input_type = Company


class HashInMISP(AttributeInMISP):
    display_name = 'Hash in MISP?'
    input_type = Hash


class DomainInMISP(AttributeInMISP):
    display_name = 'Domain in MISP?'
    input_type = Domain


class IPv4AddressInMISP(AttributeInMISP):
    display_name = 'IPv4Address in MISP?'
    input_type = IPv4Address


class URLInMISP(AttributeInMISP):
    display_name = 'URL in MISP?'
    input_type = URL


class DNSNameInMISP(AttributeInMISP):
    display_name = 'DNSName in MISP?'
    input_type = DNSName


class ASInMISP(AttributeInMISP):
    display_name = 'AS in MISP?'
    input_type = AS


class WebsiteInMISP(AttributeInMISP):
    display_name = 'Website in MISP?'
    input_type = Website


class NSRecordInMISP(AttributeInMISP):
    display_name = 'NSRecord in MISP?'
    input_type = NSRecord


class PhoneNumberInMISP(AttributeInMISP):
    display_name = 'PhoneNumber in MISP?'
    input_type = PhoneNumber


class EmailAddressInMISP(AttributeInMISP):
    display_name = 'EmailAddress in MISP?'
    input_type = EmailAddress


class FileInMISP(AttributeInMISP):
    display_name = 'File in MISP?'
    input_type = File


class HashtagInMISP(AttributeInMISP):
    display_name = 'Hashtag in MISP?'
    input_type = Hashtag


class AliasInMISP(AttributeInMISP):
    display_name = 'Alias in MISP?'
    input_type = Alias


class TwitterInMISP(AttributeInMISP):
    display_name = 'Twitter in MISP?'
    input_type = Twitter


class CompanyInMISP(AttributeInMISP):
    display_name = 'Company in MISP?'
    input_type = Company
