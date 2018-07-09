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
import datetime

import spur


class RemoteExecutor(object):
    """ Executes commands on Node instances via SSH.
        Assumes password-less setup.
    """

    PREFIX = ["sh", "-c"]

    def __init__(self, nodes=None, user="cloud-user",
                 ssh_allow_missing_host_keys=False, ssh_path_to_private_key=None):
        self.nodes = nodes or []
        self.user = user
        self.missing_host_key = (spur.ssh.MissingHostKey.accept
                                 if ssh_allow_missing_host_keys
                                 else spur.ssh.MissingHostKey.raise_error)
        self.ssh_path_to_private_key = ssh_path_to_private_key

    def execute(self, cmd, nodes=None, debug=False):
        nodes = nodes or self.nodes
        results = dict()
        cmd_full = self.PREFIX + [cmd]
        for node in nodes:
            params = {
                "hostname": node.ip,
                "username": node.sshuser,
                "missing_host_key": self.missing_host_key
            }
            if node.sshpass is None:
                params["private_key_file"] = self.ssh_path_to_private_key
            else:
                params["password"] = node.sshpass
            shell = spur.SshShell(**params)

            print("%s - Executing '%s' on %s" % (datetime.datetime.now(), cmd_full, node.name))
            try:
                with shell:
                    output = shell.run(cmd_full)
                    results[node.ip] = {
                        "ret_code": output.return_code,
                        "stdout": output.output.decode(),
                        "stderr": output.stderr_output.decode(),
                    }
            except Exception as e:
                results[node.ip] = {
                    "ret_code": 1,
                    "error": str(e),
                }
        return results
