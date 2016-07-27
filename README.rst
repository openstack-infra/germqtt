=======
germqtt
=======

Germqtt, like its name implies, is a tool for publish a gerrit event stream
into MQTT. It will publish all the capture events from the gerrit event stream
and publish them to MQTT into topics split by project and event type. For
example a commented added to a project name foo would be published as an event
on the topic: base_topic/foo/commented-added

By default germqtt is setup as a daemon however if you need to run it
interactively you can use the *--foreground* option to do this.

MQTT Topics
===========
germqtt will push gerrit events to topics broken by project and event type.
The formula used is::

  <base topic>/<project>/<event type>

For example, if gerrit emits a *comment-added* event for the *openstack/nova*
project germqtt will push that event to the topic::

  gerrit/openstack/nova/comment-added

assuming the base topic is configured to be gerrit. For more information on
topics in MQTT refer to: https://mosquitto.org/man/mqtt-7.html

Configuration
=============
There are a few required pieces of information to make germqtt work properly.
These settings are specified in the config file.

Gerrit
------

You need to provide credentials and connection information for connecting to
gerrit to get the event stream. Germqtt uses the gerritlib library to establish
a connection to gerrit over ssh and listen to the event stream. All these
options live in the *[gerrit]* section.  The 3 required options for gerrit are:

 * **username** - The username to login with
 * **hostname** - The hostname for your gerrit server
 * **key** - The path to your ssh key to use for connecting to gerrit

There is also an optional config option, *port*, which is used to specify the
port to connect to gerrit with. By default this is set to 29418, which is the
gerrit default. If your gerrit server uses a non-default port you'll need to set
this option.

MQTT
----

Just as with gerrit there are a few required options for talking to MQTT, which
is the other axis of communication in germqtt. The options for configuring MQTT
communication go in the *[mqtt]* section. The 2 required options are:

 * **hostname** - The hostname for the MQTT broker
 * **topic** - The base topic name to use for the gerrit events

There are also a couple optional settings for communicating with mqtt that you
can set:

 * **port** - The port to communicate to the MQTT broker on. By default this
              is set to 1883, the default MQTT port. This only needs to be set
              if your broker uses a non-default port.
 * **keepalive** - Used to set the keepalive time for connections to the MQTT
                   broker. By default this is set to 60 seconds.
 * **username** - Used to set the auth username to connect to the MQTT broker
                  with.
 * **password** - Used to set the auth password to connect to the MQTT broker
                  with. A username must be set for this option to be used.

Other Settings
--------------

By default germqtt will use /var/run/germqtt.pid for it's PID file, if however
you'd like to use a different file for storing the PID you can use the *pidfile*
option in the *[default]* section of the configuration file.
