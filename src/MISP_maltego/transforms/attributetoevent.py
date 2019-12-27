from canari.maltego.entities import Unknown
from canari.maltego.transform import Transform
# from canari.framework import EnableDebugWindow
from MISP_maltego.transforms.common.util import check_update, get_misp_connection, event_to_entity, object_to_entity, get_attribute_in_event, get_attribute_in_object, attribute_to_entity, get_entity_property
from canari.maltego.message import LinkDirection

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
    """Green bookmark if known in MISP"""
    input_type = Unknown
    display_name = 'in MISP?'
    remote = True

    def do_transform(self, request, response, config):
        response += check_update(config)
        maltego_misp_attribute = request.entity
        # skip MISP Events (value = int)
        try:
            int(maltego_misp_attribute.value)
            return response
        except Exception:
            pass

        misp = get_misp_connection(config, request.parameters)
        events_json = misp.search(controller='events', value=maltego_misp_attribute.value, with_attachments=False)
        # we need to do really rebuild the Entity from scratch as request.entity is of type Unknown
        for e in events_json:
            attr = get_attribute_in_event(e, maltego_misp_attribute.value)
            if attr:
                for item in attribute_to_entity(attr, only_self=True):
                    response += item
        return response


# placeholder for https://github.com/MISP/MISP-maltego/issues/11
# waiting for support of CIDR search through the REST API
# @EnableDebugWindow
# class NetblockToAttributes(Transform):
#     display_name = 'to MISP Attributes'
#     input_type = Netblock
#     remote = True

#     def do_transform(self, request, response, config):
#         maltego_misp_attribute = request.entity
#         misp = get_misp_connection(config, request.parameters)
#         import ipaddress
#         ip_start, ip_end = maltego_misp_attribute.value.split('-')
#         # FIXME make this work with IPv4 and IPv6
#         # automagically detect the different CIDRs
#         cidrs = ipaddress.summarize_address_range(ipaddress.IPv4Address(ip_start), ipaddress.IPv4Address(ip_end))
#         for cidr in cidrs:
#             print(str(cidr))
#             attr_json = misp.search(controller='attributes', value=str(cidr), with_attachments=False)
#             print(attr_json)
#         return response


# @EnableDebugWindow
class AttributeToEvent(Transform):
    input_type = Unknown
    display_name = 'to MISP Event'
    remote = True

    def do_transform(self, request, response, config):
        response += check_update(config)
        # skip some Entities
        skip = ['properties.mispevent']
        for i in skip:
            if i in request.entity.fields:
                return response

        if 'ipv4-range' in request.entity.fields:
            # placeholder for https://github.com/MISP/MISP-maltego/issues/11
            pass

        misp = get_misp_connection(config, request.parameters)
        # from Galaxy
        if 'properties.mispgalaxy' in request.entity.fields:
            tag_name = get_entity_property(request.entity, 'tag_name')
            if not tag_name:
                tag_name = request.entity.value
            events_json = misp.search(controller='events', tags=tag_name, with_attachments=False)
            for e in events_json:
                response += event_to_entity(e, link_direction=LinkDirection.OutputToInput)
            return response
        # from Object
        elif 'properties.mispobject' in request.entity.fields:
            if request.entity.fields.get('event_id'):
                events_json = misp.search(controller='events', eventid=request.entity.fields.get('event_id').value, with_attachments=False)
                for e in events_json:
                    response += event_to_entity(e, link_direction=LinkDirection.OutputToInput)
                return response
            else:
                return response
        # standard Entities (normal attributes)
        else:
            events_json = misp.search(controller='events', value=request.entity.value, with_attachments=False)

        # return the MISPEvent or MISPObject of the attribute
        for e in events_json:
            # find the value as attribute
            attr = get_attribute_in_event(e, request.entity.value)
            if attr:
                response += event_to_entity(e, link_direction=LinkDirection.OutputToInput)
            # find the value as object
            if 'Object' in e['Event']:
                for o in e['Event']['Object']:
                    if get_attribute_in_object(o, attribute_value=request.entity.value).get('value'):
                        response += object_to_entity(o, link_direction=LinkDirection.OutputToInput)

        return response
