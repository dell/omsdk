#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Copyright © 2018 Dell Inc. or its subsidiaries. All rights reserved.
# Dell, EMC, and other trademarks are trademarks of Dell Inc. or its subsidiaries.
# Other trademarks may be trademarks of their respective owners.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Vaideeswaran Ganesan
#
import xml.etree.ElementTree as ET
import re
import json
import logging
import sys, os
import glob
import threading

logger = logging.getLogger(__name__)

# Attribute Registry Convertor
#   .xml to .json file converter
class maj:
    def __init__(self):
        self.cntr = 0
        self.ids = 0
    def incr(self):
        self.cntr += 1
    def ids(self):
        self.ids += 1

class AttribRegistry(object):

    def _sanitize_name(self, fld_name, suffix):
        typName = fld_name.strip() + suffix
        typName = re.sub('^(^[0-9])', 'E_\\1', typName)
        typName = re.sub('[[]([^]:]+)[^]]*[]]', '\\1', typName)
        typName = re.sub('[?]', '', typName)
        typName = re.sub('[-.]', '_', typName)
        typName = re.sub('^[ \t]+', '', typName)
        return typName

    def get_type(self, config_spec, origtype, fname):
        types_in = config_spec['types']
        if self.comp not in types_in:
            return origtype
        for field_type in types_in[self.comp]:
            if '_' in fname:
                (field_name, group_name) = fname.split('_')
            else:
                (field_name, group_name) = (fname, 'NA')
            if group_name in types_in[self.comp][field_type] and \
                field_name in types_in[self.comp][field_type][group_name]:
                    return field_type
        return origtype

    def build_attrentry(self, regentry, all_entries, attrx_group):
        for attr in regentry:
            myentry = {}
            for attrfield in attr:
                if len(attrfield) <= 0:
                    # attribute
                    myentry [attrfield.tag] = attrfield.text
                    if attrfield.tag in ["GroupName"]:
                        if not attrfield.text in attrx_group:
                            attrx_group[attrfield.text] = []
                        attrx_group[attrfield.text].append(myentry)
                elif attrfield.tag in ["AttributeType"]:
                    if not attrfield.tag in myentry:
                        myentry[attrfield.tag] = {}
                    myentry [attrfield.tag] = attrfield.text
                elif attrfield.tag in ["AttributeValue"]:
                    if not attrfield.tag in myentry:
                        myentry[attrfield.tag] = {}
                        myentry["enum"] = []
                        myentry["enumDescriptions"] = []
                    enum_name = None
                    enum_value = None
                    for child in attrfield:
                        if (child.tag == "ValueName"):
                            if enum_value:
                                logger.debug("WARN: Duplicate value found!")
                            else:
                                enum_value = child.text
                        else:
                            if enum_name:
                                logger.debug("WARN: Duplicate name found!")
                            else:
                                enum_name = child.text
                    myentry[attrfield.tag][enum_name] = enum_value
                    myentry["enum"].append(enum_value.strip())
                    myentry["enumDescriptions"].append(enum_name)
                elif attrfield.tag in ["Modifiers"]:
                    for modifiers in attrfield:
                        if modifiers.tag in ['BrowserRead', 'BrowserWrite',
                                'BrowserSuppressed', 'ProgrammaticRead',
                                'ProgrammaticWrite']:
                            pass
                        elif modifiers.tag in ['RegEx', 'Partition']:
                            myentry[modifiers.tag] = modifiers.text
                        else:
                            logger.debug("WARN: Unknown!!" + modifiers.tag)
                else:
                    logger.debug("WARN: Unknown!!" + attrfield.tag)
            all_entries.append(myentry)

    def build_groups(self, attrx_group):
        for group in attrx_group:
            tt = self.attr_json["definitions"][self.comp]["config_groups"]
            tt[group] = []
            for ent in attrx_group[group]:
                fld_name = ent["AttributeName"]
                if self.addGroup:
                    fld_name += "_" + group
                tt[group].append(fld_name)

    def load_json(self, all_entries, comp, MAJ):
        attmap = {
            'IsReadOnly' : 'readonly',
            'DisplayName' : 'description',
            'HelpText' : 'longDescription',
            'Partition' : 'partition',
            'RegEx' : 'pattern',
            'Min' : 'min',
            'Max' : 'max',
            'GroupName' : 'qualifier',
            'AttributeName' : 'name',
            'AttributeType' : 'baseType',
            'DefaultValue' : 'default',
        }
        typemaps = {
            'integer' : 'int',
            'string' : 'str',
            'enumeration' : 'enum',

            'orderlistseq' : 'list',
            'password' : 'str',
            'binary' : 'str',
            'minmaxrange' : 'minmaxrange', # RAID, NIC - means integer
                                           # for FCHBA - means length of string
            'range' : 'int',
        }

        for entry in all_entries:
            tt = self.attr_json["definitions"][comp]["properties"]
            if entry['AttributeType'].lower() in [
                'form title', 'form ref', 'checkbox', 'formset title'
            ]: continue

            MAJ.ids += 1
            fld_name = entry["AttributeName"]
            if self.addGroup and "GroupName" in entry:
                fld_name = fld_name + "_" + entry["GroupName"]
            tt[fld_name] = {}
            for fld in attmap:
                if fld in entry:
                    if attmap[fld] in ['baseType']:
                        ntype = typemaps[entry[fld].lower()]
                        if self.comp == 'FCHBA' and ntype == 'minmaxrange':
                            ntype = 'str'
                        tt[fld_name][attmap[fld]] = ntype
                    else:
                        if entry[fld] == "FALSE": entry[fld] = False
                        if entry[fld] == "TRUE": entry[fld] = True
                        tt[fld_name][attmap[fld]] = entry[fld]

            if 'min' in tt[fld_name]:
                if self.comp == 'FCHBA' :
                    del tt[fld_name]['min']
                elif int(tt[fld_name]['min']) <= -2**63:
                        tt[fld_name]['min'] = str(-2**63)
            if 'max' in tt[fld_name]:
                if self.comp == 'FCHBA' :
                    del tt[fld_name]['max']
                elif int(tt[fld_name]['max']) >= 2**63-1:
                        tt[fld_name]['max'] = str(2**63-1)
            if 'min' not in tt[fld_name] and 'max' in tt[fld_name]:
                tt[fld_name]['min'] = str(-2**63)
            if 'max' not in tt[fld_name] and 'min' in tt[fld_name]:
                tt[fld_name]['max'] = str(2**63)

            tt[fld_name]['modDeleteAllowed'] = True
            tt[fld_name]['uneditable'] = False
            if 'readonly' in tt[fld_name] and tt[fld_name]['readonly'] in ['true']:
                if 'longDescription' in tt[fld_name] and \
                    'Configurable via XML' not in tt[fld_name]['longDescription']:
                    tt[fld_name]['uneditable'] = True
                tt[fld_name]['modDeleteAllowed'] = False

            attr_type = 'string'
            if "AttributeType" in entry:
                attr_type = entry["AttributeType"].lower()
            if "AttributeValue" in entry:
                typName = self._sanitize_name(fld_name, 'Types')
                tt[fld_name]["type"] = typName
                self.attr_json["definitions"][typName] = {
                    "enum" : entry["enum"],
                    "enumDescriptions" : entry["enumDescriptions"],
                    "type" : attr_type,
                }

    def update_type(self, comp, config_spec, MAJ):
        tt = self.attr_json["definitions"][comp]["properties"]
        for fld_name in self.attr_json["definitions"][comp]["properties"]:
            ntype = self.get_type(config_spec, tt[fld_name]['baseType'], fld_name)
            if tt[fld_name]['baseType'] != ntype:
                MAJ.incr()
                tt[fld_name]['baseType'] = ntype

    def __init__(self, file_name, dconfig, config_spec, MAJ):
        self.lock = threading.Lock()
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        regentry = None
        for regent in self.root:
            if regent.tag == "REGISTRY_ENTRIES":
                regentry = regent
                break
        self.comp = re.sub("^.*[\\\\]", "", file_name)
        self.comp = re.sub("\..*$", "", self.comp)
        self.addGroup = (self.comp == 'iDRAC')
        self.direct = re.sub("[^\\\\]+$", "", file_name)
        self.attr_json = {
            "$schema" : file_name,
            "title" : file_name,
            "$ref" : "#/definitions/" + self.comp,
            "definitions" : {
                self.comp : {
                    "config_groups" : {},
                    "type" : "object",
                    "properties" : {}
                }
            }
        }
        self.config_spec = config_spec

        attrx_group = {}
        all_entries = []
        with self.lock:
            self.build_attrentry(regentry, all_entries, attrx_group)
        for mycomp in self.config_spec:

            if 'registry' not in self.config_spec[mycomp] or \
               self.config_spec[mycomp]['registry'] != self.comp or \
               'attributes' not in self.config_spec[mycomp]:
                continue
            attrx_group[mycomp] = []
            arents = self.config_spec[mycomp]['attributes']
            for ent in all_entries:
                if ent['AttributeName'] in arents:
                    attrx_group[mycomp].append(ent)
                    ent['GroupName'] = mycomp

        with self.lock:
            self.build_groups(attrx_group)
        with self.lock:
            self.load_json(all_entries, self.comp,MAJ)
        with self.lock:
            self.update_type(self.comp, config_spec, MAJ)

        props = self.attr_json["definitions"][self.comp]["properties"]
        if 'RAIDTypes' in props:
            self.attr_json["definitions"]['RAIDTypesTypes']['enum'].append('Volume')
            self.attr_json["definitions"]['RAIDTypesTypes']['enumDescriptions'].append('Volume')

        if 'AttachState_VirtualConsole' in props:
            self.attr_json["definitions"]['AttachState_VirtualConsoleTypes']['enum'].append('Auto-Attach')
            self.attr_json["definitions"]['AttachState_VirtualConsoleTypes']['enumDescriptions'].append('Auto-Attach')
        if 'StripeSize' in props:
            props['StripeSize']['type'] = 'StripeSizeTypes'
            self.attr_json["definitions"]['StripeSizeTypes'] = {
                "enum": [
                    "Default",
                    "512",
                    "1KB", "2KB", "4KB", "8KB",
                    "16KB", "32KB", "64KB",
                    "128KB", "256KB", "512KB",
                    "1MB", "2MB", "4MB", "8MB",
                ],
                "enumDescriptions": [
                    "Default",
                    "512",
                    "1KB", "2KB", "4KB", "8KB",
                    "16KB", "32KB", "64KB",
                    "128KB", "256KB", "512KB",
                    "1MB", "2MB", "4MB", "8MB",
                ],
                "type": "string"
            }

    def save_file(self, directory = None, filename = None):
        if not directory: directory = self.direct
        if not filename: filename = self.comp + ".json"
        dest_file = os.path.join(directory, filename)
        print ("Saving to :" + dest_file)
        with open(dest_file, "w") as out:
            out.write(json.dumps(self.attr_json, sort_keys=True,
                                 indent=4, separators=(',', ': ')))

    def save_enums(self, directory = None, filename = None):
        if self.comp == 'EventFilters': return
        if not directory: directory = self.direct
        if not filename: filename = self.comp + ".py"
        dest_file = os.path.join(directory, filename)
        print('Saving to :' + dest_file)
        with open(dest_file, 'w') as out:
            out.write('from omsdk.sdkcenum import EnumWrapper\n')
            out.write('import sys\n')
            out.write('import logging\n')
            out.write('\n')
            out.write('PY2 = sys.version_info[0] == 2\n')
            out.write('PY3 = sys.version_info[0] == 3\n')
            out.write('\n')
            out.write('logger = logging.getLogger(__name__)\n')
            out.write('\n')
            props = self.attr_json
            sprops = []
            for i in props['definitions']:
                if 'enum' not in props['definitions'][i]:
                    continue
                sprops.append(i)
            sprops = sorted(sprops)

            for i in sprops:
                en_val = [k.strip() for k in props['definitions'][i]['enum']]
                en_name = []
                out.write('{0} = EnumWrapper("{0}", '.format(i) + '{\n')
                MBLOOKUP = {
                  '1KB' : 1*1024,
                  '2KB' : 2*1024,
                  '4KB' : 4*1024,
                  '8KB' : 8*1024,
                  '16KB' : 16*1024,
                  '32KB' : 32*1024,
                  '64KB' : 64*1024,
                  '128KB' : 128*1024,
                  '256KB' : 256*1024,
                  '512KB' : 512*1024,
                  '1MB' : 1*1024*1024,
                  '2MB' : 2*1024*1024,
                  '4MB' : 4*1024*1024,
                  '8MB' : 8*1024*1024,
                  'Default' : 'Default',
                  '512' : '512',
                }

                for ent in en_val:
                    en_name.append(self._sanitize(ent))
                if i == 'StripeSizeTypes':
                    t_en_val = []
                    for ent in en_val:
                        t_en_val.append(MBLOOKUP[ent])
                    en_val = t_en_val
                en_dict = dict(zip(en_name, en_val))
                snames = sorted([i for i in en_dict])
                for j in snames:
                    out.write('    "{0}" : "{1}",\n'.format(j, en_dict[j]))
                out.write('}).enum_type\n')
                out.write('\n')

    def _sanitize(self, tval):
        if tval:
            tval = re.sub('[^A-Za-z0-9]', '_', tval)
            tval = re.sub('[^A-Za-z0-9]', '_', tval)
            tval = re.sub('^(True|None|False)$', 'T_\\1', tval)
            tval = re.sub('^(^[0-9])', 'T_\\1', tval)
        return tval

    def _print(self, out, props, group, dconfig):

        # build groups!!
        new_prop_def = {}
        # group
        #   fldname
        #    ::pytype
        #        modDeleteAllowed
        #        uneditable
        #        doc
        #        type
        #        default
        #        alias
        FieldTypeMap = {
                'enum' : 'EnumTypeField',
                'str' : 'StringField',
                'int' : 'IntField',
                'bool' : 'BooleanField',
                'enum' : 'EnumTypeField',
                'list' : 'StringField', # TODO
                'minmaxrange' : 'IntRangeField', 
                'IPv4AddressField' : 'IPv4AddressField',
                'IPAddressField' : 'IPAddressField',
                'IPv6AddressField' : 'IPv6AddressField',
                'MacAddressField' : 'MacAddressField',
                'WWPNAddressField' : 'WWPNAddressField',
                'PortField' : 'PortField',
                'ListField' : 'ListField',
        }

        for i in props:
            if group: gname = props[i]['qualifier']
            else:
                gname = self.comp
                if 'alias' in self.config_spec and \
                   self.comp in self.config_spec['alias'] and \
                   isinstance(self.config_spec['alias'][self.comp], str):
                   gname = self.config_spec['alias'][self.comp]
            if not gname in new_prop_def:
                new_prop_def[gname] = {}
            if not i in new_prop_def[gname]:
                new_prop_def[gname][i] = {}

            # readonly, unediable 
            new_prop_def[gname][i]['modDeleteAllowed'] = True
            new_prop_def[gname][i]['uneditable'] = False
            if 'readonly' in props[i] and props[i]['readonly'] :

                if 'longDescription' in props[i] and \
                    'Configurable via XML' not in props[i]['longDescription']:
                    new_prop_def[gname][i]['uneditable'] = True

                new_prop_def[gname][i]['modDeleteAllowed'] = False

            # Pydoc description
            desc = i
            if 'longDescription' in props[i]:
                desc = props[i]['longDescription']
            desc = re.sub('[ \t\v\b]+', ' ', desc)
            desc = re.sub('[^[A-Za-z0-9;,.<>/:!()]" -]', "", desc)
            desc = desc.replace('"', "'")
            new_prop_def[gname][i]['doc'] = desc

            # python type
            f_pytype = FieldTypeMap[props[i]['baseType']]

            # Default processing
            if 'default' not in props[i]:
                props[i]['default'] = None

            if 'min' not in props[i]:
                props[i]['min'] = None

            if 'max' not in props[i]:
                props[i]['max'] = None

            # type and default values
            new_prop_def[gname][i]['type'] = None
            new_prop_def[gname][i]['min'] = props[i]['min']
            new_prop_def[gname][i]['max'] = props[i]['max']
            new_prop_def[gname][i]['default'] = props[i]['default']
            defval = new_prop_def[gname][i]['default']

            if defval:
                typename = None
                if 'type' in props[i]:
                    typename = props[i]['type']
                    if typename in self.attr_json["definitions"]:
                        typedef = self.attr_json['definitions'][typename]
                        if 'enum' not in typedef:
                            pass
                            #print(self.comp+'.'+typename+ ' has no enums!')
                        elif defval not in typedef['enum']:
                            typedef['enum'].append(defval)
                            typedef["enumDescriptions"].append(defval)
                            #print(defval+" added to " + self.comp+'.'+typename)
                        if len(typedef['enum']) <= 1:
                            #print(i + " is suspcious enum. has one entry!")
                            f_pytype = 'StringField'
                        elif f_pytype not in ['EnumTypeField']:
                            #print(props[i]['baseType']+" wrong enum:" + i)
                            f_pytype = 'EnumTypeField'

            if f_pytype in ['EnumTypeField']:
                if 'type' not in props[i]:
                    #print(i + " is wrong typed as enum. switching to enum!")
                    f_pytype = 'StringField'
            if f_pytype in ['IntField'] and \
              (new_prop_def[gname][i]['min'] or new_prop_def[gname][i]['max']):
                f_pytype = 'IntRangeField'

            #if o_pytype != f_pytype:
            #    print("{0} => original({1}), new({2})".format(i, o_pytype, f_pytype))
            if 'defaults' in self.config_spec and  \
               self.comp in self.config_spec['defaults'] and  \
               i in self.config_spec['defaults'][self.comp]:
               defval = self.config_spec['defaults'][self.comp][i]

            if f_pytype in ['EnumTypeField']:
                if defval:
                    defval = props[i]['type'] + '.' + self._sanitize(defval)
                else:
                    defval = str(defval)
                new_prop_def[gname][i]['type'] = props[i]['type']
            elif f_pytype in ['IntField', 'IntRangeField']:
                defval = str(defval)
            else:
                if defval:
                    defval = '"' + defval + '"'
                else:
                    defval = str(defval)
            if defval is None and f_pytype in ['StringField']:
                defval = ''
            new_prop_def[gname][i]['default'] = defval
            new_prop_def[gname][i]['pytype'] = f_pytype

            # alias:
            new_prop_def[gname][i]['alias'] = None
            new_prop_def[gname][i]['fldname'] = self._sanitize_name(i, '')
            if new_prop_def[gname][i]['fldname'] != i.strip():
                new_prop_def[gname][i]['alias'] = i

        for grp in sorted(new_prop_def.keys()):
            cls_props = list(new_prop_def[grp].keys())
            s_cls_props = sorted([i for i in cls_props])
            ngrp = self._sanitize(grp)
            out.write('class {0}(ClassType):\n'.format(ngrp))
            out.write('\n')
            out.write('    def __init__(self, parent = None, loading_from_scp=False):\n')
            if grp == self.comp or (grp in self.config_spec and grp not in ['CMC', 'NIC']):
                out.write('        if PY2: \n')
                out.write('            super({0}, self).__init__("Component", None, parent)\n'.format(ngrp))
                out.write('        else: \n')
                out.write('            super().__init__("Component", None, parent)\n')
            else:
                out.write('        if PY2: \n')
                out.write('            super({0}, self).__init__(None, "{1}", parent)\n'.format(ngrp, grp))
                out.write('        else: \n')
                out.write('            super().__init__(None, "'+grp+'", parent)\n')
            for i in s_cls_props:
                if '[Partition:n]' in i:
                    continue
                field_spec = "        self.{0} = ".format(new_prop_def[grp][i]['fldname'])
                if new_prop_def[grp][i]['pytype'] in ['StringField']:
                    new_prop_def[grp][i]['default'] = '""'
                field_spec  += "{0}({1}".format(new_prop_def[grp][i]['pytype'], new_prop_def[grp][i]['default'])
                if new_prop_def[grp][i]['type']:
                    field_spec  += ",{0}".format(new_prop_def[grp][i]['type'])
                if new_prop_def[grp][i]['min']:
                    field_spec  += ",{0}".format(new_prop_def[grp][i]['min'])
                if new_prop_def[grp][i]['max']:
                    field_spec  += ",{0}".format(new_prop_def[grp][i]['max'])
                if new_prop_def[grp][i]['alias']:
                    field_spec += ', alias="{0}"'.format(new_prop_def[grp][i]['alias'])
                field_spec += ', parent=self'
                if not new_prop_def[grp][i]['modDeleteAllowed']:
                    field_spec += ", modifyAllowed = False"
                    field_spec += ", deleteAllowed = False"
                if new_prop_def[grp][i]['uneditable']:
                    out.write('        # readonly attribute populated by iDRAC\n')
                elif not new_prop_def[grp][i]['modDeleteAllowed']:
                    out.write('        # readonly attribute\n')
                if 'reboot' in self.config_spec and grp in self.config_spec['reboot']:
                    if i in self.config_spec['reboot'][grp]:
                        field_spec += ", rebootRequired = True"
                out.write(field_spec + ')\n')

                if 'alias' in self.config_spec and \
                   self.comp in self.config_spec['alias'] and \
                   not isinstance(self.config_spec['alias'][self.comp], str) and\
                   grp in self.config_spec['alias'][self.comp]:
                    aliasobj = self.config_spec['alias'][self.comp][grp]
                    if isinstance(aliasobj, dict):
                        if i in self.config_spec['alias'][self.comp][grp]:
                            out.write('        self.{0} = self.{1}\n'.format(
                                self.config_spec['alias'][self.comp][grp][i],
                                new_prop_def[grp][i]['fldname']))
                            out.write("        self._ignore_fields('{0}')\n".format(
                                self.config_spec['alias'][self.comp][grp][i]))
            if grp in self.config_spec and 'children' in self.config_spec[grp]:
                for child in self.config_spec[grp]['children']:
                    out.write('        self.{0} = ArrayType({0}, parent=self, index_helper=FQDDHelper(), loading_from_scp=loading_from_scp)\n'.format(child, 1, 100))

            if 'composite' in self.config_spec and grp in self.config_spec['composite']:
                for field in self.config_spec['composite'][grp]:
                    fmsg = ""
                    comma = ""
                    for ent in  self.config_spec['composite'][grp][field]:
                        fmsg +=  comma + 'self.' + ent + '_' + grp
                        comma = ", "
                    out.write('        self.{0} = CompositeFieldType({1})\n'.format(field, fmsg))

            out.write('        self.commit(loading_from_scp)\n')
            out.write('\n')
            if 'arrays' in self.config_spec and grp in self.config_spec['arrays']:
                ent = self.config_spec['arrays'][grp]
                if 'key' not in ent:
                    print("ERROR: Key is not present for "+ grp)
                    ent['key'] = [ grp ]
                out.write('    @property\n')
                out.write('    def Key(self):\n')
                fmsg = ""
                comma = ""
                for field in ent['key']:
                    fmsg += comma + 'self.' + field + '_' + grp
                    comma = ", "
                if ',' in fmsg:
                    fmsg = '(' + fmsg + ')'
                out.write('        return {0}\n'.format(fmsg))
                out.write('\n')
                out.write('    @property\n')
                out.write('    def Index(self):\n')
                out.write('        return self.{0}_{1}._index\n'.format(ent['key'][0], grp))
                out.write('\n')
        if group:
            for comp in self.config_spec:
                if 'registry' not in self.config_spec[comp] or \
                   self.config_spec[comp]['registry'] != self.comp:
                    continue
                if 'groups' not in self.config_spec[comp]:
                    self.config_spec[comp]['groups'] = []
                if 'excl_groups' in self.config_spec[comp]:
                    grps = set(self.config_spec[comp]['groups']+ list(new_prop_def.keys()))
                    grps = grps - set(self.config_spec[comp]['excl_groups'])
                    self.config_spec[comp]['groups'] = grps
                if len(self.config_spec[comp]['groups']) <= 0:
                    continue
                out.write('class {0}(ClassType):\n'.format(comp))
                out.write('\n')
                out.write('    def __init__(self, parent = None, loading_from_scp=False):\n')
                out.write('        if PY2: \n')
                out.write('            super({0}, self).__init__("Component", None, parent)\n'.format(comp))
                out.write('        else: \n')
                out.write('            super().__init__("Component", None, parent)\n')
                for grp in sorted(self.config_spec[comp]['groups']):
                    ngrp = self._sanitize(grp)
                    if 'arrays' in self.config_spec and grp in self.config_spec['arrays']:
                        ent = self.config_spec['arrays'][grp]
                        out.write('        self.{0} = ArrayType({0}, parent=self, index_helper =IndexHelper({1}, {2}), loading_from_scp=loading_from_scp)\n'.format(ngrp, ent['min'], ent['max']))


                    else:
                        out.write('        self.{0} = {0}(parent=self, loading_from_scp=loading_from_scp)\n'.format(ngrp))

                out.write('        self.commit(loading_from_scp)\n')
                out.write('\n')

    def save_types(self, directory, dconfig, group):
        if self.comp == 'EventFilters': return
        if not directory: directory = self.direct
        filename = self.comp + ".py"
        dest_file = os.path.join(directory, filename)
        print('Saving to :' + dest_file)
        self.device = 'iDRAC'

        with open(dest_file, 'w') as out:
            props = self.attr_json['definitions'][self.comp]['properties']
            out.write('from omdrivers.enums.{0}.{1} import *\n'.format(self.device, self.comp))
            out.write('from omsdk.typemgr.ClassType import ClassType\n')
            out.write('from omsdk.typemgr.ArrayType import ArrayType, IndexHelper\n')
            out.write('from omsdk.typemgr.BuiltinTypes import *\n')
            out.write('import sys\n')
            out.write('import logging\n')
            out.write('\n')
            out.write('PY2 = sys.version_info[0] == 2\n')
            out.write('PY3 = sys.version_info[0] == 3\n')
            out.write('\n')
            out.write('logger = logging.getLogger(__name__)\n')
            out.write('\n')

            self._print(out, props, group, dconfig)

def save_tree(directory, dconfig, device):
    if not directory: directory = self.direct
    if 'tree' not in config_spec:
        print("No tree found in config spec")
        return
    for elem in config_spec['tree']:
        filename = elem + ".py"
        dest_file = os.path.join(directory, filename)
        print('Saving to :' + dest_file)
        registries = []
        for i in config_spec:
            if 'registry' in config_spec[i] and config_spec[i]['registry']:
                registries.append(config_spec[i]['registry'])
        registries = set(registries)
        comps = config_spec['tree'][elem]

        with open(dest_file, 'w') as out:
            out.write('from omsdk.typemgr.ClassType import ClassType\n')
            out.write('from omsdk.typemgr.ArrayType import ArrayType, IndexHelper\n')
            out.write('from omsdk.typemgr.BuiltinTypes import RootClassType\n')
            for i in registries:
                out.write('from omdrivers.types.{0}.{1} import *\n'.format(device, i))
            out.write('import sys\n')
            out.write('import logging\n')
            out.write('\n')
            out.write('PY2 = sys.version_info[0] == 2\n')
            out.write('PY3 = sys.version_info[0] == 3\n')
            out.write('\n')
            out.write('logger = logging.getLogger(__name__)\n')
            out.write('\n')

            out.write('class {0}(RootClassType):\n'.format(elem))
            out.write('\n')
            out.write('    def __init__(self, parent = None, loading_from_scp=False):\n')
            out.write('        if PY2:\n')
            out.write('            super({0}, self).__init__("{0}", None, parent)\n'.format(elem))
            out.write('        else:\n')
            out.write('            super().__init__("{0}", None, parent)\n'.format(elem))

            for comp in comps:
                if comp not in config_spec or \
                   'entries' not in config_spec[comp]:
                    print(comp + " not found!")
                    continue
                if config_spec[comp]['entries'] == 1:
                    out.write('        self.{0} = {0}(parent=self, loading_from_scp=loading_from_scp)\n'.format(comp))
                else:
                    comp0 = comp
                    if comp == 'NetworkInterface': comp0 = 'NIC'
                    out.write('        self.{0} = ArrayType({1}, parent=self, loading_from_scp=loading_from_scp)\n'.format(comp0, comp))

            out.write("        self._ignore_attribs('ServiceTag', 'Model', 'TimeStamp')\n")
            out.write('        self.commit(loading_from_scp)\n')
            out.write('\n')

def do_dump(file1, dconfig, config_spec, group, MAJ):
    ar= AttribRegistry(file1, dconfig, config_spec, MAJ)
    ar.save_file(directory=dconfig)
    ar.save_types(types_dir, dconfig, group)
    # types would have added unknown enumerations!
    ar.save_enums(directory=os.path.join('omdrivers', 'enums', 'iDRAC'))

if __name__ == "__main__":
    MAJ = maj()
    device = 'iDRAC'
    driver_dir = os.path.join('omdrivers', device)
    types_dir = os.path.join('omdrivers', 'types', device)
    dconfig = os.path.join(driver_dir, 'Config')
    f_config_spec = os.path.join(dconfig, 'iDRAC.comp_spec')
    config_spec = {}
    if os.path.exists(f_config_spec):
        with open(f_config_spec) as f:
            config_spec = json.load(f)
    for file1 in glob.glob(os.path.join(driver_dir, "xml", "*.xml")):
        print("Processing: " + file1)
        if file1.endswith('EventFilters.xml') is True: continue
        do_dump(file1, dconfig, config_spec, file1.endswith('iDRAC.xml') or file1.endswith('RAID.xml'), MAJ)
    save_tree(types_dir, dconfig, device)
    print(str(MAJ.cntr) + " objects have special types")
    print(str(MAJ.ids) + " attributes created!")
