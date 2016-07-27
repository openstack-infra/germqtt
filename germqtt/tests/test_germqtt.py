# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from germqtt import germqtt
from germqtt.tests import base


class TestGermqtt(base.TestCase):

    def test_get_topic_with_project(self):
        base_topic = 'gerrit'
        event = {
            'project': 'fake_project',
            'type': 'fake-type',
        }
        full_topic = germqtt.get_topic(base_topic, event)
        self.assertEqual('gerrit/fake_project/fake-type', full_topic)
