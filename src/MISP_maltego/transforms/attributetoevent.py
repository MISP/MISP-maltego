from canari.maltego.entities import Unknown, Hashtag
from canari.maltego.transform import Transform
from MISP_maltego.transforms.common.entities import MISPGalaxy
from MISP_maltego.transforms.common.util import check_update, MISPConnection, event_to_entity, get_attribute_in_event, get_attribute_in_object, attribute_to_entity, get_entity_property, search_galaxy_cluster, galaxycluster_to_entity
from canari.maltego.message import LinkDirection, Bookmark

__author__ = 'Christophe Vandeplas'
__copyright__ = 'Copyright 2018, MISP_maltego Project'
__credits__ = []

__license__ = 'AGPLv3'
__version__ = '0.1'
__maintainer__ = 'Christophe Vandeplas'
__email__ = 'christophe@vandeplas.com'
__status__ = 'Development'


class SearchInMISP(Transform):
    """Use % at the front/end for wildcard search"""
    input_type = Unknown
    display_name = 'Search in MISP'
    description = "Use % at the front/end for wildcard search"
    remote = True

    def do_transform(self, request, response, config):
        response += check_update(config)
        link_label = 'Search result'

        if 'properties.mispevent' in request.entity.fields:
            conn = MISPConnection(config, request.parameters)
            # if event_id
            try:
                if request.entity.value == '0':
                    return response
                eventid = int(request.entity.value)
                events_json = conn.misp.search(controller='events', eventid=eventid, with_attachments=False)
                for e in events_json:
                    response += event_to_entity(e, link_label=link_label, link_direction=LinkDirection.OutputToInput)
                return response
            except ValueError:
                pass
            # if event_info string as value
            events_json = conn.misp.search(controller='events', eventinfo=request.entity.value, with_attachments=False)
            for e in events_json:
                response += event_to_entity(e, link_label=link_label, link_direction=LinkDirection.OutputToInput)
            return response

        # From galaxy or Hashtag
        if 'properties.mispgalaxy' in request.entity.fields or 'properties.temp' in request.entity.fields or 'twitter.hashtag' in request.entity.fields:
            if request.entity.value == '-':
                return response
            # First search in galaxies
            keyword = get_entity_property(request.entity, 'Temp')
            if not keyword:
                keyword = request.entity.value
            # assume the user is searching for a cluster based on a substring.
            # Search in the list for those that match and return galaxy entities'
            potential_clusters = search_galaxy_cluster(keyword)
            # LATER check if duplicates are possible
            if potential_clusters:
                for potential_cluster in potential_clusters:
                    new_entity = galaxycluster_to_entity(potential_cluster, link_label=link_label)
                    # LATER support the type_filter - unfortunately this is not possible, we need Canari to tell us the original entity type
                    if isinstance(new_entity, MISPGalaxy):
                        response += new_entity

            # from Hashtag search also in tags
            if 'properties.temp' in request.entity.fields or 'twitter.hashtag' in request.entity.fields:
                keyword = get_entity_property(request.entity, 'Temp')
                if not keyword:
                    keyword = request.entity.value
                conn = MISPConnection(config, request.parameters)
                result = conn.misp.direct_call('tags/search', {'name': keyword})
                for t in result:
                    # skip misp-galaxies as we have processed them earlier on
                    if t['Tag']['name'].startswith('misp-galaxy'):
                        continue
                    # In this case we do not filter away those we add as notes, as people might want to pivot on it explicitly.
                    response += Hashtag(t['Tag']['name'], link_label=link_label, bookmark=Bookmark.Green)

            return response

        # for all other normal entities
        conn = MISPConnection(config, request.parameters)

        # we need to do really rebuild the Entity from scratch as request.entity is of type Unknown
        # TODO First try to build the object, then only attributes (for those that are not in object, or for all?)
        # TODO check for the right version of MISP before, it needs to be 2.4.127 or higher.
        # obj_json = conn.misp.search(controller='objects', value=request.entity.value, with_attachments=False)
        # for o in obj_json:
        #         for item in attribute_to_entity(attr, only_self=True, link_label=link_label):
        #             response += item
        #     # find the value as object, and return the object
        #     if 'Object' in e['Event']:
        #         for o in e['Event']['Object']:
        #             if get_attribute_in_object(o, attribute_value=request.entity.value, substring=True).get('value'):
        #                 response += conn.object_to_entity(o, link_label=link_label)

        attr_json = conn.misp.search(controller='attributes', value=request.entity.value, with_attachments=False)
        for a in attr_json['Attribute']:
            for item in attribute_to_entity(a, only_self=True, link_label=link_label):
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
#         # LATER make this work with IPv4 and IPv6
#         # automagically detect the different CIDRs
#         cidrs = ipaddress.summarize_address_range(ipaddress.IPv4Address(ip_start), ipaddress.IPv4Address(ip_end))
#         for cidr in cidrs:
#             print(str(cidr))
#             attr_json = misp.search(controller='attributes', value=str(cidr), with_attachments=False)
#             print(attr_json)
#         return response


class AttributeToEvent(Transform):
    input_type = Unknown
    display_name = 'To MISP Events'
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

        conn = MISPConnection(config, request.parameters)
        # from Galaxy
        if 'properties.mispgalaxy' in request.entity.fields:
            tag_name = get_entity_property(request.entity, 'tag_name')
            if not tag_name:
                tag_name = request.entity.value
            events_json = conn.misp.search(controller='events', tags=tag_name, with_attachments=False)
            for e in events_json:
                response += event_to_entity(e, link_direction=LinkDirection.OutputToInput)
            return response
        # from Object
        elif 'properties.mispobject' in request.entity.fields:
            if request.entity.fields.get('event_id'):
                events_json = conn.misp.search(controller='events', eventid=request.entity.fields.get('event_id').value, with_attachments=False)
                for e in events_json:
                    response += event_to_entity(e, link_direction=LinkDirection.OutputToInput)
                return response
            else:
                return response
        # from Hashtag
        elif 'properties.temp' in request.entity.fields or 'twitter.hashtag' in request.entity.fields:
            tag_name = get_entity_property(request.entity, 'Temp')
            if not tag_name:
                tag_name = request.entity.value
            events_json = conn.misp.search_index(tags=tag_name)
            for e in events_json:
                response += event_to_entity({'Event': e}, link_direction=LinkDirection.OutputToInput)
            return response
        # standard Entities (normal attributes)
        else:
            events_json = conn.misp.search(controller='events', value=request.entity.value, with_attachments=False)

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
                        response += conn.object_to_entity(o, link_direction=LinkDirection.OutputToInput)

        return response
