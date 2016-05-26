#! /usr/bin/env python

# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import ConfigParser
import logging
import json
import os

import daemon
import gerritlib.gerrit
import paho.mqtt.publish as publish

try:
    import daemon.pidlockfile
    pid_file_module = daemon.pidlockfile
except Exception:
    # as of python-daemon 1.6 it doesn't bundle pidlockfile anymore
    # instead it depends on lockfile-0.9.1
    import daemon.pidfile
    pid_file_module = daemon.pidfile


log = logging.getLogger('germqtt')

class GerritStream(object):

    def __init__(self, user, host, key, thread=True, port=29418):
        self.gerrit = gerritlib.gerrit.Gerrit(host, user, port, key)
        if thread:
            self.gerrit.startWatching()

    def get_event(self):
        return self.gerrit.getEvent()


class PushMQTT(object):
    def __init__(self, hostname, port=1883, client_id=None,
                 keepalive=60, will=None, auth=None, tls=None):
        self.hostname = hostname
        self.port = port
        self.client_id = client_id
        self.keepalive = 60
        self.will = will
        self.auth = auth
        self.tls = tls

    def publish_single(self, topic, msg):
        publish.single(topic, msg, hostname=self.hostname,
                       port=self.port, client_id=self.client_id,
                       keepalive=self.keepalive, will=self.will,
                       auth=self.auth, tls=self.tls)

    def publish_multiple(self, topic, msg):
        publish.multiple(topic, msg, hostname=self.hostname,
                         port=self.port, client_id=self.client_id,
                         keepalive=self.keepalive, will=self.will,
                         auth=self.auth, tls=self.tls)


def get_options():
    parser = argparse.ArgumentParser(
        description="Daemon to publish a gerrit event stream on MQTT")
    parser.add_argument('-f', '--foreground',
                        default=False,
                        action='store_true',
                        help="Run in foreground")
    parser.add_argument('conffile', nargs=1, help="Configuration file")
    return parser.parse_args()

def get_topic(base_topic, event):
    project = event.get('project', '')
    event_type = event.get('type', '')
    pieces = [base_topic, project, event_type]
    topic = "/".join(pieces)
    return topic


def _main(args, config):
    if config.has_option('gerrit', 'port'):
        port = config.get('gerrit', 'port')
    else:
        port = 29418
    gerrit = GerritStream(
        config.get('gerrit', 'username'),
        config.get('gerrit', 'hostname'),
        config.get('gerrit', 'key'),
        port=port)

    if config.has_option('mqtt', 'port'):
        mqtt_port = config.get('mqtt', 'port')
    else:
        mqtt_port = 1883
    if config.has_option('mqtt', 'keepalive'):
        keepalive = config.get('mqtt', 'keepalive')
    else:
        keepalive = 60

    mqttqueue = PushMQTT(
        config.get('mqtt', 'hostname'),
        port=mqtt_port,
        keepalive=keepalive)

    base_topic = config.get('mqtt', 'topic')
    while True:
        event = gerrit.get_event()
        topic = get_topic(base_topic, event)
        if event:
            mqttqueue.publish_single(topic, json.dumps(event))


def main():
    args = get_options()
    config = ConfigParser.ConfigParser()
    config.read(args.conffile)

    if config.has_option('default', 'pidfile'):
        pid_fn = os.path.expanduser(config.get('default', 'pidfile'))
    else:
        pid_fn = '/var/run/germqtt.pid'

    if args.foreground:
        _main(args, config)
    else:
        pid = pid_file_module.TimeoutPIDLockFile(pid_fn, 10)
        with daemon.DaemonContext(pidfile=pid):
            _main(args, config)

if __name__ == "__main__":
    main()
