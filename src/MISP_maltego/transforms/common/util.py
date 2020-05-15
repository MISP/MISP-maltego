from canari.maltego.entities import Hash, URL, File, Person, Hashtag
from canari.maltego.message import Label, LinkStyle, MaltegoException, Bookmark, LinkDirection, UIMessage, UIMessageType
from canari.mode import is_local_exec_mode, is_remote_exec_mode
from distutils.version import StrictVersion
from MISP_maltego.transforms.common.entities import MISPEvent, MISPObject, MISPGalaxy
from MISP_maltego.transforms.common.mappings import mapping_object_icon, mapping_misp_to_maltego, mapping_galaxy_icon, mapping_galaxy_type
from pymisp import ExpandedPyMISP as PyMISP
import json
import os
import os.path
import requests
import tempfile
import time

# FIXME from galaxy 'to MISP Event' is confusing

__version__ = '1.4.4'  # also update version in setup.py

tag_note_prefixes = ['tlp:', 'PAP:', 'de-vs:', 'euci:', 'fr-classif:', 'nato:']

update_url = 'https://raw.githubusercontent.com/MISP/MISP-maltego/master/setup.py'
local_path_root = os.path.join(tempfile.gettempdir(), 'MISP-maltego')
local_path_version = os.path.join(local_path_root, 'versioncheck')
if not os.path.exists(local_path_root):
    os.mkdir(local_path_root)
    os.chmod(local_path_root, mode=0o777)  # temporary workaround - see https://github.com/redcanari/canari3/issues/61


def check_update(config):
    # Do not check updates if running as remote transform
    if is_remote_exec_mode():
        return None
    # only raise the alert once a day/reboot to the user.
    try:
        if time.time() - os.path.getmtime(local_path_version) > 60 * 60 * 24:  # check the timestamp of the file
            recheck = True
        else:
            recheck = False
    except Exception:  # file does not exist, so check version
        recheck = True
    if not recheck:
        return None
    # remember we checked the version
    from pathlib import Path
    Path(local_path_version).touch()
    # UIMessageType must be Fatal as otherwise it is not shown to the user.
    if 'MISP_maltego.local.check_updates' not in config:
        return UIMessage("'check_updates' parameter missing in '.canari/MISP_maltego.conf'. Please set 'check_updates = True/False'.", type=UIMessageType.Fatal)
    if config['MISP_maltego.local.check_updates']:
        # check the version
        r = requests.get(update_url)
        for l in r.text.splitlines():
            if 'version=' in l:
                online_ver = l.strip().strip(',').split('=').pop().strip("'")
                if StrictVersion(online_ver) > StrictVersion(__version__):
                    message = ('A new version of MISP-Maltego is available.\n'
                               'To upgrade, please:\n'
                               '    pip3 --upgrade MISP-maltego'
                               '    canari create-profile MISP_maltego\n'
                               '    And import the newly generated .mtz bundle in Maltego (Import > Import Configuration)')
                    return UIMessage(message, type=UIMessageType.Fatal)
                break
    return None


class MISPConnection():
    def __init__(self, config=None, parameters=None):
        self.misp = None

        if not config:
            raise MaltegoException("ERROR: MISP connection not yet established, and config not provided as parameter.")
        misp_verify = True
        misp_debug = False
        misp_url = None
        misp_key = None
        try:
            if is_local_exec_mode():
                misp_url = config['MISP_maltego.local.misp_url']
                misp_key = config['MISP_maltego.local.misp_key']
                if config['MISP_maltego.local.misp_verify'] in ['False', 'false', 0, 'no', 'No']:
                    misp_verify = False
                if config['MISP_maltego.local.misp_debug'] in ['True', 'true', 1, 'yes', 'Yes']:
                    misp_debug = True
            else:
                try:
                    misp_url = parameters['mispurl'].value
                    misp_key = parameters['mispkey'].value
                except AttributeError:
                    raise MaltegoException("ERROR: mispurl and mispkey need to be set to something valid")
            self.misp = PyMISP(misp_url, misp_key, misp_verify, 'json', misp_debug, tool='misp_maltego')
        except Exception:
            if is_local_exec_mode():
                raise MaltegoException("ERROR: Cannot connect to MISP server. Please verify your MISP_Maltego.conf settings.")
            else:
                raise MaltegoException("ERROR: Cannot connect to MISP server. Please verify your settings (MISP URL and API key), and ensure the MISP server is reachable from the internet.")

    def object_to_entity(self, o, link_label=None, link_direction=LinkDirection.InputToOutput):
        # find a nice icon for it
        try:
            icon_url = mapping_object_icon[o['name']]
        except KeyError:
            # it's not in our mapping, just ignore and leave the default icon
            icon_url = None
        # Generate a human readable display-name:
        # - find the first RequiredOneOf that exists
        # - if none, use the first RequiredField
        # LATER further finetune the human readable version of this object
        o_template = self.misp.get_object_template(o['template_uuid'])
        human_readable = None
        try:
            found = False
            while not found:  # the while loop is broken once something is found, or the requiredOneOf has no elements left
                required_ote_type = o_template['ObjectTemplate']['requirements']['requiredOneOf'].pop(0)
                for ote in o_template['ObjectTemplateElement']:
                    if ote['object_relation'] == required_ote_type:
                        required_a_type = ote['type']
                        break
                for a in o['Attribute']:
                    if a['type'] == required_a_type:
                        human_readable = '{}:\n{}'.format(o['name'], a['value'])
                        found = True
                        break
        except Exception:
            pass
        if not human_readable:
            try:
                found = False
                parts = []
                for required_ote_type in o_template['ObjectTemplate']['requirements']['required']:
                    for ote in o_template['ObjectTemplateElement']:
                        if ote['object_relation'] == required_ote_type:
                            required_a_type = ote['type']
                            break
                    for a in o['Attribute']:
                        if a['type'] == required_a_type:
                            parts.append(a['value'])
                            break
                human_readable = '{}:\n{}'.format(o['name'], '|'.join(parts))
            except Exception:
                human_readable = o['name']
        return MISPObject(
            human_readable,
            uuid=o['uuid'],
            event_id=int(o['event_id']),
            meta_category=o.get('meta_category'),
            description=o.get('description'),
            comment=o.get('comment'),
            icon_url=icon_url,
            link_label=link_label,
            link_direction=link_direction,
            bookmark=Bookmark.Green
        )

    def object_to_relations(self, o, e):
        # process forward and reverse references, so just loop over all the objects of the event
        if 'Object' in e['Event']:
            for eo in e['Event']['Object']:
                if 'ObjectReference' in eo:
                    for ref in eo['ObjectReference']:
                        # we have found original object. Expand to the related object and attributes
                        if eo['uuid'] == o['uuid']:
                            # the reference is an Object
                            if ref.get('Object'):
                                # get the full object in the event, as our objectReference included does not contain everything we need
                                sub_object = get_object_in_event(ref['Object']['uuid'], e)
                                yield self.object_to_entity(sub_object, link_label=ref['relationship_type'])
                            # the reference is an Attribute
                            if ref.get('Attribute'):
                                ref['Attribute']['event_id'] = ref['event_id']   # LATER remove this ugly workaround - object can't be requested directly from MISP using the uuid, and to find a full object we need the event_id
                                for item in attribute_to_entity(ref['Attribute'], link_label=ref['relationship_type']):
                                    yield item

                        # reverse-lookup - this is another objects relating the original object
                        if ref['referenced_uuid'] == o['uuid']:
                            yield self.object_to_entity(eo, link_label=ref['relationship_type'], link_direction=LinkDirection.OutputToInput)


def entity_obj_to_entity(entity_obj, v, t, **kwargs):
    if entity_obj == Hash:
        return entity_obj(v, _type=t, **kwargs)  # LATER type is conflicting with type of Entity, Report this as bug see line 326 /usr/local/lib/python3.5/dist-packages/canari/maltego/entities.py

    return entity_obj(v, **kwargs)


def get_entity_property(entity, name):
    for k, v in entity.fields.items():
        if k == name:
            return v.value
    return None


def attribute_to_entity(a, link_label=None, event_tags=[], only_self=False):
    # prepare some attributes to a better form
    a['data'] = None  # empty the file content as we really don't need this here
    if a['type'] == 'malware-sample':
        a['type'] = 'filename|md5'
    if a['type'] == 'regkey|value':  # LATER regkey|value => needs to be a special non-combined object
        a['type'] = 'regkey'

    combined_tags = event_tags
    if 'Galaxy' in a and not only_self:
        for g in a['Galaxy']:
            for c in g['GalaxyCluster']:
                yield galaxycluster_to_entity(c)

    # complement the event tags with the attribute tags.
    if 'Tag' in a and not only_self:
            for t in a['Tag']:
                combined_tags.append(t['name'])
                # ignore all misp-galaxies
                if t['name'].startswith('misp-galaxy'):
                    continue
                # ignore all those we add as notes
                if tag_matches_note_prefix(t['name']):
                    continue
                yield Hashtag(t['name'], bookmark=Bookmark.Green)

    notes = convert_tags_to_note(combined_tags)

    # special cases
    if a['type'] in ('url', 'uri'):
        yield(URL(url=a['value'], short_title=a['value'], link_label=link_label, notes=notes, bookmark=Bookmark.Green))
        return

    # attribute is from an object, and a relation gives better understanding of the type of attribute
    if a.get('object_relation') and mapping_misp_to_maltego.get(a['object_relation']):
        entity_obj = mapping_misp_to_maltego[a['object_relation']][0]
        yield entity_obj(a['value'], labels=[Label('comment', a.get('comment'))], link_label=link_label, notes=notes, bookmark=Bookmark.Green)

    # combined attributes
    elif '|' in a['type']:
        t_1, t_2 = a['type'].split('|')
        v_1, v_2 = a['value'].split('|')
        if t_1 in mapping_misp_to_maltego:
            entity_obj = mapping_misp_to_maltego[t_1][0]
            labels = [Label('comment', a.get('comment'))]
            if entity_obj == File:
                labels.append(Label('hash', v_2))
            yield entity_obj_to_entity(entity_obj, v_1, t_1, labels=labels, link_label=link_label, notes=notes, bookmark=Bookmark.Green)  # LATER change the comment to include the second part of the regkey
        if t_2 in mapping_misp_to_maltego:
            entity_obj = mapping_misp_to_maltego[t_2][0]
            labels = [Label('comment', a.get('comment'))]
            if entity_obj == Hash:
                labels.append(Label('filename', v_1))
            yield entity_obj_to_entity(entity_obj, v_2, t_2, labels=labels, link_label=link_label, notes=notes, bookmark=Bookmark.Green)  # LATER change the comment to include the first part of the regkey

    # normal attributes
    elif a['type'] in mapping_misp_to_maltego:
        entity_obj = mapping_misp_to_maltego[a['type']][0]
        yield entity_obj_to_entity(entity_obj, a['value'], a['type'], labels=[Label('comment', a.get('comment'))], link_label=link_label, notes=notes, bookmark=Bookmark.Green)

    # not supported in our maltego mapping are not handled

    # LATER : relationships from attributes - not yet supported by MISP yet, but there are references in the datamodel


def object_to_attributes(o, e):
    # first process attributes from an object that belong together (eg: first-name + last-name), and remove them from the list
    if o['name'] == 'person':
        first_name = get_attribute_in_object(o, attribute_type='first-name', drop=True).get('value')
        last_name = get_attribute_in_object(o, attribute_type='last-name', drop=True).get('value')
        yield entity_obj_to_entity(Person, ' '.join([first_name, last_name]).strip(), 'person', lastname=last_name, firstnames=first_name, bookmark=Bookmark.Green)

    # process normal attributes
    for a in o['Attribute']:
        for item in attribute_to_entity(a):
            yield item


def get_object_in_event(uuid, e):
    for o in e['Event']['Object']:
        if o['uuid'] == uuid:
            return o


def get_attribute_in_object(o, attribute_type=False, attribute_value=False, drop=False, substring=False):
    '''Gets the first attribute of a specific type within an object'''
    found_attribute = {'value': ''}
    for i, a in enumerate(o['Attribute']):
        if a['type'] == attribute_type:
            found_attribute = a.copy()
            if drop:    # drop the attribute from the object
                o['Attribute'].pop(i)
            break
        if a['value'] == attribute_value:
            found_attribute = a.copy()
            if drop:    # drop the attribute from the object
                o['Attribute'].pop(i)
            break
        if '|' in a['type'] or a['type'] == 'malware-sample':
            if attribute_value in a['value'].split('|'):
                found_attribute = a.copy()
                if drop:    # drop the attribute from the object
                    o['Attribute'].pop(i)
                break
        # TODO implement substring matching
        if substring:
            keyword = attribute_value.strip('%')
            if attribute_value.startswith('%') and attribute_value.endswith('%'):
                if attribute_value in a['value']:
                    found_attribute = a.copy()
                    if drop:    # drop the attribute from the object
                        o['Attribute'].pop(i)
                    break
                if '|' in a['type'] or a['type'] == 'malware-sample':
                    val1, val2 = a['value'].split('|')
                    if attribute_value in val1 or attribute_value in val2:
                        found_attribute = a.copy()
                        if drop:    # drop the attribute from the object
                            o['Attribute'].pop(i)
                        break
            elif attribute_value.startswith('%'):
                if a['value'].endswith(keyword):
                    found_attribute = a.copy()
                    if drop:    # drop the attribute from the object
                        o['Attribute'].pop(i)
                    break
                if '|' in a['type'] or a['type'] == 'malware-sample':
                    val1, val2 = a['value'].split('|')
                    if val1.endswith(keyword) or val2.endswith(keyword):
                        found_attribute = a.copy()
                        if drop:    # drop the attribute from the object
                            o['Attribute'].pop(i)
                        break

            elif attribute_value.endswith('%'):
                if a['value'].startswith(keyword):
                    return a
                if '|' in a['type'] or a['type'] == 'malware-sample':
                    val1, val2 = a['value'].split('|')
                    if val1.startswith(keyword) or val2.startswith(keyword):
                        found_attribute = a.copy()
                        if drop:    # drop the attribute from the object
                            o['Attribute'].pop(i)
                        break
    return found_attribute


def get_attribute_in_event(e, attribute_value, substring=False):
    for a in e['Event']["Attribute"]:
        if a['value'] == attribute_value:
            return a
        if '|' in a['type'] or a['type'] == 'malware-sample':
            if attribute_value in a['value'].split('|'):
                return a
        if substring:
            keyword = attribute_value.strip('%')
            if attribute_value.startswith('%') and attribute_value.endswith('%'):
                if attribute_value in a['value']:
                    return a
                if '|' in a['type'] or a['type'] == 'malware-sample':
                    val1, val2 = a['value'].split('|')
                    if attribute_value in val1 or attribute_value in val2:
                        return a
            elif attribute_value.startswith('%'):
                if a['value'].endswith(keyword):
                    return a
                if '|' in a['type'] or a['type'] == 'malware-sample':
                    val1, val2 = a['value'].split('|')
                    if val1.endswith(keyword) or val2.endswith(keyword):
                        return a

            elif attribute_value.endswith('%'):
                if a['value'].startswith(keyword):
                    return a
                if '|' in a['type'] or a['type'] == 'malware-sample':
                    val1, val2 = a['value'].split('|')
                    if val1.startswith(keyword) or val2.startswith(keyword):
                        return a

    return None


def convert_tags_to_note(tags):
    if not tags:
        return None
    notes = []
    for tag in tags:
        for tag_note_prefix in tag_note_prefixes:
            if tag.startswith(tag_note_prefix):
                notes.append(tag)
    return '\n'.join(notes)


def tag_matches_note_prefix(tag):
    for tag_note_prefix in tag_note_prefixes:
        if tag.startswith(tag_note_prefix):
            return True
    return False


def event_to_entity(e, link_style=LinkStyle.Normal, link_label=None, link_direction=LinkDirection.InputToOutput):
    tags = []
    if 'Tag' in e['Event']:
        for t in e['Event']['Tag']:
            tags.append(t['name'])
    notes = convert_tags_to_note(tags)
    return MISPEvent(
        e['Event']['id'],
        uuid=e['Event']['uuid'],
        info=e['Event']['info'],
        link_style=link_style,
        link_label=link_label,
        link_direction=link_direction,
        count_attributes=len(e['Event'].get('Attribute') or ""),
        count_objects=len(e['Event'].get('Object') or ""),
        notes=notes,
        bookmark=Bookmark.Green)


def galaxycluster_to_entity(c, link_label=None, link_direction=LinkDirection.InputToOutput):
    if 'meta' in c and 'uuid' in c['meta']:
        c['uuid'] = c['meta']['uuid'].pop(0)

    if 'meta' in c and 'synonyms' in c['meta']:
        synonyms = ', '.join(c['meta']['synonyms'])
    else:
        synonyms = ''

    galaxy_cluster = get_galaxy_cluster(uuid=c['uuid'])
    # map the 'icon' name from the cluster to the icon filename of the intelligence-icons repository
    try:
        icon_url = mapping_galaxy_icon[galaxy_cluster['icon']]
    except KeyError:
        # it's not in our mapping, just ignore and leave the default icon
        icon_url = None

    # create the right sub-galaxy: ThreatActor, Software, AttackTechnique, ... or MISPGalaxy
    try:
        galaxy_type = mapping_galaxy_type[galaxy_cluster['type']]
    except KeyError:
        galaxy_type = MISPGalaxy
    return galaxy_type(
        '{}\n{}'.format(c['type'], c['value']),
        uuid=c['uuid'],
        description=c.get('description'),
        cluster_type=c.get('type'),
        cluster_value=c.get('value'),
        synonyms=synonyms,
        tag_name=c['tag_name'],
        link_label=link_label,
        icon_url=icon_url,
        link_direction=link_direction
    )


# LATER this uses the galaxies from github as the MISP web UI does not fully support the Galaxies in the webui.
# See https://github.com/MISP/MISP/issues/3801
galaxy_archive_url = 'https://github.com/MISP/misp-galaxy/archive/master.zip'
local_path_uuid_mapping = os.path.join(local_path_root, 'MISP_maltego_galaxy_mapping.json')
local_path_clusters = os.path.join(local_path_root, 'misp-galaxy-master', 'clusters')
galaxy_cluster_uuids = None


def galaxy_update_local_copy(force=False):
    import io
    import json
    import os
    import requests
    from zipfile import ZipFile

    # some aging and automatic re-downloading
    if not os.path.exists(local_path_uuid_mapping):
        force = True
    else:
        # force update if cache is older than 24 hours
        if time.time() - os.path.getmtime(local_path_uuid_mapping) > 60 * 60 * 24:
            force = True

    if force:
        # create a lock to prevent two processes doing the same, and writing to the file at the same time
        lockfile = local_path_uuid_mapping + '.lock'
        from pathlib import Path
        while os.path.exists(lockfile):
            time.sleep(0.3)
        Path(local_path_uuid_mapping + '.lock').touch()
        # download the latest zip of the public galaxy
        try:
            resp = requests.get(galaxy_archive_url)
            zf = ZipFile(io.BytesIO(resp.content))
            zf.extractall(local_path_root)
            zf.close()
        except Exception:
            raise(MaltegoException("ERROR: Could not download Galaxy data from htts://github.com/MISP/MISP-galaxy/. Please check internet connectivity."))

        # generate the uuid mapping and save it to a file
        galaxies_fnames = []
        for f in os.listdir(local_path_clusters):
            if '.json' in f:
                galaxies_fnames.append(f)
        galaxies_fnames.sort()

        cluster_uuids = {}
        for galaxy_fname in galaxies_fnames:
            try:
                fullPathClusters = os.path.join(local_path_clusters, galaxy_fname)
                with open(fullPathClusters) as fp:
                    galaxy = json.load(fp)
                with open(fullPathClusters.replace('clusters', 'galaxies')) as fg:
                    galaxy_main = json.load(fg)
                for cluster in galaxy['values']:
                    if 'uuid' not in cluster:
                        continue
                    # skip deprecated galaxies/clusters
                    if galaxy_main['namespace'] == 'deprecated':
                        continue
                    # keep track of the cluster, but also enhance it to look like the cluster we receive when accessing the web.
                    cluster_uuids[cluster['uuid']] = cluster
                    cluster_uuids[cluster['uuid']]['type'] = galaxy['type']
                    cluster_uuids[cluster['uuid']]['tag_name'] = 'misp-galaxy:{}="{}"'.format(galaxy['type'], cluster['value'])
                    if 'icon' in galaxy_main:
                        cluster_uuids[cluster['uuid']]['icon'] = galaxy_main['icon']
            except Exception:
                # we ignore incorrect galaxies
                pass

        with open(local_path_uuid_mapping, 'w') as f:
            json.dump(cluster_uuids, f)
        # remove the lock
        os.remove(lockfile)


def galaxy_load_cluster_mapping():
    galaxy_update_local_copy()
    with open(local_path_uuid_mapping, 'r') as f:
        cluster_uuids = json.load(f)
    return cluster_uuids


def get_galaxy_cluster(uuid=None, tag=None, request_entity=None):
    global galaxy_cluster_uuids
    if not galaxy_cluster_uuids:
        galaxy_cluster_uuids = galaxy_load_cluster_mapping()

    if uuid:
        return galaxy_cluster_uuids.get(uuid)
    if tag:
        for item in galaxy_cluster_uuids.values():
            if item['tag_name'] == tag:
                return item
    if request_entity:
        if request_entity.uuid:
            return get_galaxy_cluster(uuid=request_entity.uuid)
        elif request_entity.tag_name:
            return get_galaxy_cluster(tag=request_entity.tag_name)
        elif request_entity.name:
            return get_galaxy_cluster(tag=request_entity.name)


def search_galaxy_cluster(keyword):
    keyword = keyword.lower()
    global galaxy_cluster_uuids
    if not galaxy_cluster_uuids:
        galaxy_cluster_uuids = galaxy_load_cluster_mapping()

    # % only at start
    if keyword.startswith('%') and not keyword.endswith('%'):
        keyword = keyword.strip('%')
        for item in galaxy_cluster_uuids.values():
            if item['value'].lower().endswith(keyword):
                yield item
            else:
                if 'meta' in item and 'synonyms' in item['meta']:
                    for synonym in item['meta']['synonyms']:
                        if synonym.lower().endswith(keyword):
                            yield item

    # % only at end
    elif keyword.endswith('%') and not keyword.startswith('%'):
        keyword = keyword.strip('%')
        for item in galaxy_cluster_uuids.values():
            if item['value'].lower().startswith(keyword):
                yield item
            else:
                if 'meta' in item and 'synonyms' in item['meta']:
                    for synonym in item['meta']['synonyms']:
                        if synonym.lower().startswith(keyword):
                            yield item

    # search substring assuming % at start and end
    else:
        keyword = keyword.strip('%')
        for item in galaxy_cluster_uuids.values():
            if keyword in item['value'].lower():
                yield item
            else:
                if 'meta' in item and 'synonyms' in item['meta']:
                    for synonym in item['meta']['synonyms']:
                        if keyword in synonym.lower():
                            yield item


def get_galaxies_relating(uuid):
    global galaxy_cluster_uuids
    if not galaxy_cluster_uuids:
        galaxy_cluster_uuids = galaxy_load_cluster_mapping()

    for item in galaxy_cluster_uuids.values():
        if 'related' in item:
            for related in item['related']:
                if related['dest-uuid'] == uuid:
                    yield item
