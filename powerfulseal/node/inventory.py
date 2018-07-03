# Copyright 2017 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
import configparser


def read_inventory_file_to_dict(inventory_filename):
    """ Reads inventory file in ini format (for example in Ansible format),
        returns a dictionary, where keys correspond to lower case sections,
        and resolved first level-inclusions
    """
    config = configparser.ConfigParser(allow_no_value=True, delimiters=" ")
    config.read(inventory_filename)

    _groups = {}
    with open(inventory_filename) as f:
        lines = f.readlines()
        section_name = ""
        for line in lines:
            line = line.rstrip()
            if line.startswith("[") and line.endswith("]"):
                section_name = line.lstrip("[").rstrip("]")
                _groups[section_name] = []
                continue
            if len(line) == 0:
                continue
            pieces = line.split(" ")
            data = {}
            data["addr"] = pieces[0]
            for piece in pieces[1:]:
                if piece == " ":
                    continue
                k, v = piece.split("=")
                data[k] = v
            _groups[section_name].append(data)

    return _groups



