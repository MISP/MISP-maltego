from canari.maltego.transform import Transform
# from canari.framework import EnableDebugWindow
from MISP_maltego.transforms.common.entities import MISPEvent, MISPGalaxy
from MISP_maltego.transforms.common.util import get_misp_connection, galaxycluster_to_entity, get_galaxy_cluster
from canari.maltego.message import UIMessageType, UIMessage


__author__ = 'Christophe Vandeplas'
__copyright__ = 'Copyright 2018, MISP_maltego Project'
__credits__ = []

__license__ = 'AGPLv3'
__version__ = '0.1'
__maintainer__ = 'Christophe Vandeplas'
__email__ = 'christophe@vandeplas.com'
__status__ = 'Development'


# @EnableDebugWindow
class GalaxyToEvents(Transform):
    """Expands a Galaxy to multiple MISP Events."""

    # The transform input entity type.
    input_type = MISPGalaxy

    def do_transform(self, request, response, config):
        maltego_misp_galaxy = request.entity
        misp = get_misp_connection(config)
        if maltego_misp_galaxy.tag_name:
            tag_name = maltego_misp_galaxy.tag_name
        else:
            tag_name = maltego_misp_galaxy.value
        events_json = misp.search(controller='events', tags=tag_name, withAttachments=False)
        for e in events_json['response']:
            response += MISPEvent(e['Event']['id'], uuid=e['Event']['uuid'], info=e['Event']['info'])
        return response

    def on_terminate(self):
        """This method gets called when transform execution is prematurely terminated. It is only applicable for local
        transforms. It can be excluded if you don't need it."""
        pass


# @EnableDebugWindow
class GalaxyToRelations(Transform):
    """Expans a Galaxy to related Galaxies and Clusters"""
    input_type = MISPGalaxy

    def do_transform(self, request, response, config):
        maltego_misp_galaxy = request.entity

        # # FIXME if not found, send message to user to update, while noting local galaxies are not supported yet
        current_cluster = get_galaxy_cluster(maltego_misp_galaxy.uuid)
        if not current_cluster:
            response += UIMessage("Galaxy Cluster UUID not in local mapping. Please update local cache; or non-public UUID", type=UIMessageType.Inform)
            return response

        if 'related' in current_cluster:
            for related in current_cluster['related']:
                related_cluster = get_galaxy_cluster(related['dest-uuid'])
                if related_cluster:
                    response += galaxycluster_to_entity(related_cluster, link_label=related['type'])
        return response
