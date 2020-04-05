from canari.maltego.message import Entity, IntegerEntityField, StringEntityField, MatchingRule

__author__ = 'Christophe Vandeplas'
__copyright__ = 'Copyright 2018, MISP_maltego Project'
__credits__ = []

__license__ = 'AGPLv3'
__version__ = '0.1'
__maintainer__ = 'Christophe Vandeplas'
__email__ = 'christophe@vandeplas.com'
__status__ = 'Development'

__all__ = [
    'MISPEvent',
    'MISPObject',
    'MISPGalaxy',
    'ThreatActor',
    'Software',
    'AttackTechnique'
]


class MISPEvent(Entity):
    _category_ = 'MISP'
    _namespace_ = 'misp'

    icon_url = 'file://MISP_maltego/resources/images/MISPEvent.png'
    uuid = StringEntityField('uuid', display_name='UUID', matching_rule=MatchingRule.Loose)
    id = IntegerEntityField('id', display_name='id', is_value=True)
    # date = DateEntityField('type.date', display_name='Event date')
    info = StringEntityField('info', display_name='Event info', matching_rule=MatchingRule.Loose)
    # threat_level = EnumEntityField('type.enum', choices=['Undefined', 'Low', 'Medium', 'High'], display_name='Threat Level')
    # analysis = EnumEntityField('type.enum', choices=['Initial', 'Ongoing', 'Completed'])
    # org = StringEntityField('type.str', display_name='Organisation')
    count_attributes = IntegerEntityField('count_attributes', display_name="# attributes", matching_rule=MatchingRule.Loose)
    count_objects = IntegerEntityField('count_objects', display_name="# objects", matching_rule=MatchingRule.Loose)


class MISPObject(Entity):
    _category_ = 'MISP'
    _namespace_ = 'misp'

    icon_url = 'file://MISP_maltego/resources/images/MISPObject.png'
    uuid = StringEntityField('uuid', display_name='UUID')
    event_id = IntegerEntityField('event_id', display_name='Event ID')  # LATER remove this once MISP provides objects correctly when requesting only the object.  See https://github.com/MISP/MISP/issues/3801
    name = StringEntityField('name', display_name='Name', is_value=True)
    meta_category = StringEntityField('meta_category', display_name='Meta Category', matching_rule=MatchingRule.Loose)
    description = StringEntityField('description', display_name='Description', matching_rule=MatchingRule.Loose)
    comment = StringEntityField('comment', display_name='Comment', matching_rule=MatchingRule.Loose)


class MISPGalaxy(Entity):
    _category_ = 'MISP'
    _namespace_ = 'misp'

    uuid = StringEntityField('uuid', display_name='UUID', matching_rule=MatchingRule.Loose)
    name = StringEntityField('name', display_name='Name', is_value=True, matching_rule=MatchingRule.Loose)
    description = StringEntityField('description', display_name='Description', matching_rule=MatchingRule.Loose)
    cluster_type = StringEntityField('galaxy_type', display_name='Type', matching_rule=MatchingRule.Loose)
    cluster_value = StringEntityField('value', display_name='Value', matching_rule=MatchingRule.Loose)
    synonyms = StringEntityField('synonyms', display_name='Synonyms', matching_rule=MatchingRule.Loose)
    tag_name = StringEntityField('tag_name', display_name='Tag')


class ThreatActor(MISPGalaxy):
    _category_ = 'MISP'
    _namespace_ = 'misp'


class Software(MISPGalaxy):
    _category_ = 'MISP'
    _namespace_ = 'misp'


class AttackTechnique(MISPGalaxy):
    _category_ = 'MISP'
    _namespace_ = 'misp'
