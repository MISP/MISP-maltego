from canari.maltego.entities import Unknown, Hash, Domain, IPv4Address, URL, DNSName, AS, Website, NSRecord, PhoneNumber, EmailAddress, File, Person, Hashtag, Location, Company, Alias, Port, Twitter
from MISP_maltego.transforms.common.entities import MISPEvent, MISPObject, MISPGalaxy
from canari.maltego.message import UIMessageType, UIMessage, Label
from pymisp import PyMISP
import json
import tempfile
import os


# mapping_maltego_to_misp = {
#     'maltego.Hash': ['md5', 'sha1', 'sha256', 'sha224', 'sha384', 'sha512', 'sha512/224', 'sha512/256'],
#     # 'maltego.Banner': [''],
#     # 'maltego.WebTitle': [''],
#     'maltego.Domain': ['domain', 'hostname'],
#     # 'maltego.Netblock': [''],
#     # 'maltego.MXRecord': [''],
#     'maltego.IPv4Address': ['ip-src', 'ip-dst', 'ip'],
#     'maltego.URL': ['url', 'uri'],
#     'maltego.DNSName': ['domain', 'hostname'],
#     'maltego.AS': ['AS'],
#     # 'maltego.UniqueIdentifier': [''],
#     'maltego.Website': ['domain', 'hostname'],
#     'maltego.NSRecord': ['domain', 'hostname'],
#     # 'maltego.Document': [''],
#     'maltego.PhoneNumber': ['phone-number'],
#     'maltego.EmailAddress': ['email-src', 'email-dst'],
#     # 'maltego.Image': [''],  # LATER file image
#     # 'maltego.Phrase': [''],
#     'maltego.File': ['filename'],
#     # 'maltego.Person': [''],
#     # 'maltego.Sentiment': [''],
#     # 'maltego.Alias': [''],
#     # 'maltego.GPS': [''],
#     # 'maltego.CircularArea': [''],
#     # 'maltego.NominatimLocation': [''],
#     # 'maltego.Location': [''],
#     # 'maltego.Device': [''],
#     # 'maltego.affiliation.Flickr': [''],
#     # 'maltego.FacebookObject': [''],
#     # 'maltego.hashtag': [''],
#     # 'maltego.affiliation.Twitter': [''],
#     # 'maltego.affiliation.Facebook': [''],
#     # 'maltego.Twit': [''],
#     # 'maltego.Port': [''],
#     # 'maltego.Service': [''],
#     # 'maltego.BuiltWithTechnology': [''],
# }

# mapping_misp_to_maltego = {}
# for key, vals in mapping_maltego_to_misp.items():
#     for val in vals:
#         if val not in mapping_misp_to_maltego:
#             mapping_misp_to_maltego[val] = []
#         mapping_misp_to_maltego[val].append(key)

mapping_misp_to_maltego = {
    'AS': [AS],
    'domain': [Domain, NSRecord, Website, DNSName],
    'email-dst': [EmailAddress],
    'email-src': [EmailAddress],
    'filename': [File],
    'hostname': [Website, NSRecord, Domain, DNSName],
    'ip': [IPv4Address],
    'ip-dst': [IPv4Address],
    'ip-src': [IPv4Address],
    'md5': [Hash],
    'phone-number': [PhoneNumber],
    'sha1': [Hash],
    'sha224': [Hash],
    'sha256': [Hash],
    'sha384': [Hash],
    'sha512': [Hash],
    'sha512/224': [Hash],
    'sha512/256': [Hash],
    'ssdeep': [Hash],
    'impfuzzy': [Hash],
    'uri': [URL],
    'url': [URL],

    'whois-registrant-email': [EmailAddress],
    'country-of-residence': [Location],
    'github-organisation': [Company],
    'github-username': [Alias],
    'imphash': [Hash],
    'jabber-id': [Alias],
    'passport-country': [Location],
    'place-of-birth': [Location],
    'port': [Port],
    'target-email': [EmailAddress],
    'target-location': [Location],
    'target-org': [Company],
    'target-user': [Alias],
    'twitter-id': [Twitter],
    # object mappings
    'nameserver': [NSRecord],
    # FIXME add more object mappings
    # custom types created internally for technical reasons
    # 'rekey_value': [Unknown]
}


def get_misp_connection(config):
    if config['MISP_maltego.local.misp_verify'] in ['True', 'true', 1, 'yes', 'Yes']:
        misp_verify = True
    else:
        misp_verify = False
    if config['MISP_maltego.local.misp_debug'] in ['True', 'true', 1, 'yes', 'Yes']:
        misp_debug = True
    else:
        misp_debug = False
    return PyMISP(config['MISP_maltego.local.misp_url'], config['MISP_maltego.local.misp_key'], misp_verify, 'json', misp_debug)


def entity_obj_to_entity(entity_obj, v, t, **kwargs):
    if entity_obj == Hash:
        return entity_obj(v, _type=t, **kwargs)  # FIXME type is conflicting with type of Entity, Report this as bug see line 326 /usr/local/lib/python3.5/dist-packages/canari/maltego/entities.py

    return entity_obj(v, **kwargs)


def attribute_to_entity(a):
    # prepare some attributes to a better form
    a['data'] = None  # empty the file content as we really don't need this here  # FIXME feature request for misp.get_event() to not get attachment content
    if a['type'] == 'malware-sample':
        a['type'] = 'filename|md5'
    if a['type'] == 'regkey|value':
        a['type'] = 'regkey'
    # FIXME regkey|value => needs to be a special non-combined object

    # attribute is from an object, and a relation gives better understanding of the type of attribute
    if a.get('object_relation') and mapping_misp_to_maltego.get(a['object_relation']):
        entity_obj = mapping_misp_to_maltego[a['object_relation']][0]
        yield entity_obj(a['value'], labels=[Label('comment', a['comment'])])

    # combined attributes
    elif '|' in a['type']:
        t_1, t_2 = a['type'].split('|')
        v_1, v_2 = a['value'].split('|')
        if t_1 in mapping_misp_to_maltego:
            entity_obj = mapping_misp_to_maltego[t_1][0]
            labels = [Label('comment', a['comment'])]
            if entity_obj == File:
                labels.append(Label('hash', v_2))
            yield entity_obj_to_entity(entity_obj, v_1, t_1, labels=labels)  # TODO change the comment to include the second part of the regkey
        else:
            yield UIMessage("Type {} of combined type {} not supported for attribute: {}".format(t_1, a['type'], a), type=UIMessageType.Inform)
        if t_2 in mapping_misp_to_maltego:
            entity_obj = mapping_misp_to_maltego[t_2][0]
            labels = [Label('comment', a['comment'])]
            if entity_obj == Hash:
                labels.append(Label('filename', v_1))
            yield entity_obj_to_entity(entity_obj, v_2, t_2, labels=labels)  # TODO change the comment to include the first part of the regkey
        else:
            yield UIMessage("Type {} of combined type {} not supported for attribute: {}".format(t_2, a['type'], a), type=UIMessageType.Inform)

    # normal attributes
    elif a['type'] in mapping_misp_to_maltego:
        entity_obj = mapping_misp_to_maltego[a['type']][0]
        yield entity_obj_to_entity(entity_obj, a['value'], a['type'], labels=[Label('comment', a['comment'])])

    # not supported in our maltego mapping
    else:
        yield Unknown(a['value'], type=a['type'], labels=[Label('comment', a['comment'])])
        yield UIMessage("Type {} not fully supported for attribute: {}".format(a['type'], a), type=UIMessageType.Inform)

    if 'Galaxy' in a:
        for g in a['Galaxy']:
            for c in g['GalaxyCluster']:
                yield galaxycluster_to_entity(c)

    if 'Tag' in a:
            for t in a['Tag']:
                # ignore all misp-galaxies
                if t['name'].startswith('misp-galaxy'):
                    continue
                yield Hashtag(t['name'])


def object_to_entity(o):
    return MISPObject(
        o['name'],
        uuid=o['uuid'],
        event_id=int(o['event_id']),
        meta_category=o.get('meta_category'),
        description=o['description'],
        comment=o['comment']
    )


def object_to_attributes(o):
    # first process attributes from an object that belong together (eg: first-name + last-name), and remove them from the list
    if o['name'] == 'person':
        first_name = get_attribute_in_object(o, 'first-name', drop=True).get('value')
        last_name = get_attribute_in_object(o, 'last-name', drop=True).get('value')
        yield entity_obj_to_entity(Person, ' '.join([first_name, last_name]).strip(), 'person', lastname=last_name, firstnames=first_name)

    # process normal attributes
    for a in o['Attribute']:
        for item in attribute_to_entity(a):
            yield item


def get_attribute_in_object(o, attribute_type, drop=False):
    '''Gets the first attribute of a specific type within an object'''
    found_attribute = {'value': ''}
    for i, a in enumerate(o['Attribute']):
        if a['type'] == attribute_type:
            found_attribute = a.copy()
            if drop:    # drop the attribute from the object
                o['Attribute'].pop(i)
            break
    return found_attribute


def event_to_entity(e):
    return MISPEvent(e['Event']['id'], uuid=e['Event']['uuid'], info=e['Event']['info'])


def galaxycluster_to_entity(c, link_label=None):
    # print(json.dumps(c, sort_keys=True, indent=4))
    if c['meta'].get('synonyms'):
        synonyms = ', '.join(c['meta']['synonyms'])
    else:
        synonyms = ''
    return MISPGalaxy(
        '{}\n{}'.format(c['type'], c['value']),
        uuid=c['uuid'],
        description=c['description'],
        cluster_type=c['type'],
        cluster_value=c['value'],
        synonyms=synonyms,
        tag_name=c['tag_name'],
        link_label=link_label
    )


# FIXME this uses the galaxies from github as the MISP web UI does not fully support the Galaxies in the webui.
# See https://github.com/MISP/MISP/issues/3801
galaxy_archive_url = 'https://github.com/MISP/misp-galaxy/archive/master.zip'
local_path_root = os.path.join(tempfile.gettempdir(), 'MISP-maltego')
local_path_uuid_mapping = os.path.join(local_path_root, 'MISP_maltego_galaxy_mapping.json')
local_path_clusters = os.path.join(local_path_root, 'misp-galaxy-master', 'clusters')
galaxy_cluster_uuids = None


def galaxy_update_local_copy(force=False):
    import io
    import json
    import os
    import requests
    from zipfile import ZipFile

    # FIXME put some aging and automatic re-downloading
    if not os.path.exists(local_path_root):
        os.mkdir(local_path_root)
        force = True

    if force:
        # download the latest zip of the public galaxy
        resp = requests.get(galaxy_archive_url)
        zf = ZipFile(io.BytesIO(resp.content))
        zf.extractall(local_path_root)
        zf.close()

        # generate the uuid mapping and save it to a file
        galaxies_fnames = []
        for f in os.listdir(local_path_clusters):
            if '.json' in f:
                galaxies_fnames.append(f)
        galaxies_fnames.sort()

        cluster_uuids = {}
        for galaxy_fname in galaxies_fnames:
            fullPathClusters = os.path.join(local_path_clusters, galaxy_fname)
            with open(fullPathClusters) as fp:
                galaxy = json.load(fp)
            for cluster in galaxy['values']:
                # print(cluster['uuid'])
                if 'uuid' not in cluster:
                    continue
                # keep track of the cluster, but also enhance it to look like the cluster we receive when accessing the web.
                cluster_uuids[cluster['uuid']] = cluster
                cluster_uuids[cluster['uuid']]['type'] = galaxy['type']
                cluster_uuids[cluster['uuid']]['tag_name'] = 'misp-galaxy:{}="{}"'.format(galaxy['type'], cluster['value'])

        with open(local_path_uuid_mapping, 'w') as f:
            json.dump(cluster_uuids, f, sort_keys=True, indent=4)


def galaxy_load_cluster_mapping():
    galaxy_update_local_copy()
    with open(local_path_uuid_mapping, 'r') as f:
        cluster_uuids = json.load(f)
    return cluster_uuids


def get_galaxy_cluster(uuid):
    global galaxy_cluster_uuids
    if not galaxy_cluster_uuids:
        galaxy_cluster_uuids = galaxy_load_cluster_mapping()

    return galaxy_cluster_uuids.get(uuid)
