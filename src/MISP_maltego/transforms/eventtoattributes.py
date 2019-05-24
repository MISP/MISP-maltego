from canari.maltego.entities import Hashtag
from canari.maltego.transform import Transform
# from canari.framework import EnableDebugWindow
from MISP_maltego.transforms.common.entities import MISPEvent, MISPObject
from MISP_maltego.transforms.common.util import get_misp_connection, attribute_to_entity, event_to_entity, galaxycluster_to_entity, object_to_entity, object_to_attributes, object_to_relations, tag_matches_note_prefix
from canari.maltego.message import LinkStyle


__author__ = 'Christophe Vandeplas'
__copyright__ = 'Copyright 2018, MISP_maltego Project'
__credits__ = []

__license__ = 'AGPLv3'
__version__ = '0.1'
__maintainer__ = 'Christophe Vandeplas'
__email__ = 'christophe@vandeplas.com'
__status__ = 'Development'


class EventToTransform(Transform):
    input_type = None
    """Generic EventTo class containing multiple reusable functions for the subclasses."""

    def __init__(self):
        self.request = None
        self.response = None
        self.config = None
        self.misp = None
        self.event_json = None
        self.event_tags = None

    def do_transform(self, request, response, config):
        self.request = request
        self.response = response
        self.config = config
        maltego_misp_event = request.entity
        self.misp = get_misp_connection(config)
        self.event_json = self.misp.get_event(maltego_misp_event.id)  # FIXME get it without attachments # FIXME use search + includeAttachments:0, eventid: as request body
        if not self.event_json.get('Event'):
            return False

        self.response += event_to_entity(self.event_json)
        return True

    def gen_response_tags(self, gen_response=True):
        self.event_tags = []
        if 'Tag' in self.event_json['Event']:
            for t in self.event_json['Event']['Tag']:
                self.event_tags.append(t['name'])
                # ignore all misp-galaxies
                if t['name'].startswith('misp-galaxy'):
                    continue
                # ignore all those we add as notes
                if tag_matches_note_prefix(t['name']):
                    continue
                if gen_response:
                    self.response += Hashtag(t['name'])

    def gen_response_galaxies(self):
        for g in self.event_json['Event']['Galaxy']:
            for c in g['GalaxyCluster']:
                self.response += galaxycluster_to_entity(c)

    def gen_response_attributes(self):
        if not self.event_tags:
            self.gen_response_tags(gen_response=False)
        for a in self.event_json['Event']["Attribute"]:
            for entity in attribute_to_entity(a, event_tags=self.event_tags):
                if entity:
                    self.response += entity

    def gen_response_objects(self):
        for o in self.event_json['Event']['Object']:
            self.response += object_to_entity(o)

    def gen_response_relations(self):
        for e in self.event_json['Event']['RelatedEvent']:
            self.response += event_to_entity(e, link_style=LinkStyle.DashDot)


# @EnableDebugWindow
class EventToAll(EventToTransform):
    input_type = MISPEvent
    description = 'Expands an Event to Attributes, Objects, Tags, Galaxies'

    def do_transform(self, request, response, config):
        if super().do_transform(request, response, config):
            self.gen_response_tags()
            self.gen_response_galaxies()
            self.gen_response_attributes()
            self.gen_response_objects()

        return self.response


# @EnableDebugWindow
class EventToAttributes(EventToTransform):
    input_type = MISPEvent
    description = 'Expands an Event to Attributes'

    def do_transform(self, request, response, config):
        if super().do_transform(request, response, config):
            self.gen_response_attributes()

        return self.response


# @EnableDebugWindow
class EventToTags(EventToTransform):
    input_type = MISPEvent
    description = 'Expands an Event to Tags and Galaxies'

    def do_transform(self, request, response, config):
        if super().do_transform(request, response, config):
            self.gen_response_tags()
            self.gen_response_galaxies()

        return self.response


# @EnableDebugWindow
class EventToGalaxies(EventToTransform):
    input_type = MISPEvent
    description = 'Expands an Event to Galaxies'

    def do_transform(self, request, response, config):
        if super().do_transform(request, response, config):
            self.gen_response_galaxies()

        return self.response


# @EnableDebugWindow
class EventToObjects(EventToTransform):
    input_type = MISPEvent
    description = 'Expands an Event to Objects'

    def do_transform(self, request, response, config):
        if super().do_transform(request, response, config):
            self.gen_response_objects()

        return self.response


# @EnableDebugWindow
class EventToRelations(EventToTransform):
    input_type = MISPEvent
    description = 'Expands an Event to related Events'

    def do_transform(self, request, response, config):
        if super().do_transform(request, response, config):
            self.gen_response_relations()

        return self.response


# @EnableDebugWindow
class ObjectToAttributes(Transform):
    """"Expands an object to its attributes"""
    input_type = MISPObject
    description = 'Expands an Object to Attributes'

    def do_transform(self, request, response, config):
        maltego_object = request.entity
        misp = get_misp_connection(config)
        event_json = misp.get_event(maltego_object.event_id)
        for o in event_json['Event']['Object']:
            if o['uuid'] == maltego_object.uuid:
                for entity in object_to_attributes(o, event_json):
                    if entity:
                        response += entity
                for entity in object_to_relations(o, event_json):
                    if entity:
                        response += entity

        return response


# @EnableDebugWindow
class ObjectToRelations(Transform):
    """Expands an object to the relations of the object"""
    input_type = MISPObject
    description = 'Expands an Object to Relations'

    def do_transform(self, request, response, config):
        maltego_object = request.entity
        misp = get_misp_connection(config)
        event_json = misp.get_event(maltego_object.event_id)
        for o in event_json['Event']['Object']:
            if o['uuid'] == maltego_object.uuid:
                for entity in object_to_relations(o, event_json):
                    if entity:
                        response += entity

        return response
