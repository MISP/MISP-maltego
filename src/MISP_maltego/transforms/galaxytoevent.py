from canari.maltego.transform import Transform
from MISP_maltego.transforms.common.entities import MISPEvent, MISPGalaxy, ThreatActor, Software, AttackTechnique
from MISP_maltego.transforms.common.util import check_update, MISPConnection, galaxycluster_to_entity, get_galaxy_cluster, get_galaxies_relating, search_galaxy_cluster, mapping_galaxy_icon
from canari.maltego.message import UIMessageType, UIMessage, LinkDirection


__author__ = 'Christophe Vandeplas'
__copyright__ = 'Copyright 2018, MISP_maltego Project'
__credits__ = []

__license__ = 'AGPLv3'
__version__ = '0.1'
__maintainer__ = 'Christophe Vandeplas'
__email__ = 'christophe@vandeplas.com'
__status__ = 'Development'


class GalaxyToTransform(Transform):
    input_type = None

    def do_transform(self, request, response, config, type_filter=MISPGalaxy):
        response += check_update(config)

        current_cluster = get_galaxy_cluster(request_entity=request.entity)

        # legacy - replaced by Search in MISP
        if not current_cluster and request.entity.name != '-':
            # maybe the user is searching for a cluster based on a substring.
            # Search in the list for those that match and return galaxy entities
            potential_clusters = search_galaxy_cluster(request.entity.name)
            if potential_clusters:
                for potential_cluster in potential_clusters:
                    new_entity = galaxycluster_to_entity(potential_cluster, link_label='Search result')
                    if isinstance(new_entity, type_filter):
                        response += new_entity
                return response
        # end of legacy

        if not current_cluster:
            response += UIMessage("Galaxy Cluster UUID not in local mapping. Please update local cache; non-public UUID are not supported yet.", type=UIMessageType.Inform)
            return response
        c = current_cluster

        # update existing object
        galaxy_cluster = get_galaxy_cluster(uuid=c['uuid'])
        icon_url = None
        if 'icon' in galaxy_cluster:  # map the 'icon' name from the cluster to the icon filename of the intelligence-icons repository
            try:
                icon_url = mapping_galaxy_icon[galaxy_cluster['icon']]
            except Exception:
                # it's not in our mapping, just ignore and leave the default Galaxy icon
                pass
        if c['meta'].get('synonyms'):
            synonyms = ', '.join(c['meta']['synonyms'])
        else:
            synonyms = ''
        request.entity.name = '{}\n{}'.format(c['type'], c['value'])
        request.entity.uuid = c['uuid']
        request.entity.description = c.get('description')
        request.entity.cluster_type = c.get('type')
        request.entity.cluster_value = c.get('value')
        request.entity.synonyms = synonyms
        request.entity.tag_name = c['tag_name']
        request.entity.icon_url = icon_url
        # response += request.entity

        # find related objects
        if 'related' in current_cluster:
            for related in current_cluster['related']:
                related_cluster = get_galaxy_cluster(uuid=related['dest-uuid'])
                if related_cluster:
                    new_entity = galaxycluster_to_entity(related_cluster, link_label=related['type'])
                    if isinstance(new_entity, type_filter):
                        response += new_entity
        # find objects that are relating to this one
        for related in get_galaxies_relating(current_cluster['uuid']):
            related_link_label = ''
            for rel_in_rel in related['related']:
                if rel_in_rel['dest-uuid'] == current_cluster['uuid']:
                    related_link_label = rel_in_rel['type']
                    break
            new_entity = galaxycluster_to_entity(related, link_label=related_link_label, link_direction=LinkDirection.OutputToInput)
            if isinstance(new_entity, type_filter):
                response += new_entity
        return response


class GalaxyToRelations(GalaxyToTransform):
    input_type = MISPGalaxy
    display_name = 'To Related Galaxies'
    remote = True

    def do_transform(self, request, response, config, type_filter=MISPGalaxy):
        return super().do_transform(request, response, config, type_filter)


class GalaxyToSoftware(GalaxyToTransform):
    input_type = MISPGalaxy
    display_name = 'To Malware/Software/Tools'
    remote = True

    def do_transform(self, request, response, config, type_filter=Software):
        return super().do_transform(request, response, config, type_filter)


class GalaxyToThreatActor(GalaxyToTransform):
    input_type = MISPGalaxy
    display_name = 'To Threat Actors'
    remote = True

    def do_transform(self, request, response, config, type_filter=ThreatActor):
        return super().do_transform(request, response, config, type_filter)


class GalaxyToAttackTechnique(GalaxyToTransform):
    input_type = MISPGalaxy
    display_name = 'To Attack Techniques'
    remote = True

    def do_transform(self, request, response, config, type_filter=AttackTechnique):
        return super().do_transform(request, response, config, type_filter)
