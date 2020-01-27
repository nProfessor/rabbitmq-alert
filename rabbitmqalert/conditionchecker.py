#! /usr/bin/python2
# -*- coding: utf-8 -*-

import time

class ConditionChecker:

    def __init__(self, log, client, notifier_object):
        self.log = log
        self.client = client
        self.notifier = notifier_object
        self.checked = {}

    def check_queue_conditions(self, arguments):
        response = self.client.get_queue()
        if response is None:
            return

        messages_ready = response.get("messages_ready")
        messages_unacknowledged = response.get("messages_unacknowledged")
        messages = response.get("messages")
        consumers = response.get("consumers")

        queue = arguments["server_queue"]
        queue_conditions = arguments["conditions"][queue]
        ready_size = queue_conditions.get("conditions_ready_queue_size")
        unack_size = queue_conditions.get("conditions_unack_queue_size")
        total_size = queue_conditions.get("conditions_total_queue_size")
        consumers_connected_min = queue_conditions.get("conditions_queue_consumers_connected")

        wait = self.get_time_to_wait(arguments)

        if ready_size is not None and messages_ready > ready_size:
            if self.needNotify(queue + '__' + 'messages_ready', wait):
                self.notifier.send_notification("%s: messages_ready = %d > %d" % (queue, messages_ready, ready_size))
                self.clean(queue + '__' + 'messages_ready')
        else:
            self.clean(queue + '__' + 'messages_ready')

        if unack_size is not None and messages_unacknowledged > unack_size:
            if self.needNotify(queue + '__' + 'messages_unacknowledged', wait):
                self.notifier.send_notification("%s: messages_unacknowledged = %d > %d" % (queue, messages_unacknowledged, unack_size))
                self.clean(queue + '__' + 'messages_unacknowledged')
        else:
            self.clean(queue + '__' + 'messages_unacknowledged')

        if total_size is not None and messages > total_size:
            if self.needNotify(queue + '__' + 'messages', wait):
                self.notifier.send_notification("%s: messages = %d > %d" % (queue, messages, total_size))
                self.clean(queue + '__' + 'messages')
        else:
            self.clean(queue + '__' + 'messages')

        if consumers_connected_min is not None and consumers < consumers_connected_min:
            if self.needNotify(queue + '__' + 'consumers_connected', wait):
                self.notifier.send_notification("%s: consumers_connected = %d < %d" % (queue, consumers, consumers_connected_min))
                self.clean(queue + '__' + 'consumers_connected')
        else:
            self.clean(queue + '__' + 'consumers_connected')

    def check_consumer_conditions(self, arguments):
        response = self.client.get_consumers()
        if response is None:
            return

        consumers_connected = len(response)
        consumers_connected_min = arguments["generic_conditions"].get("conditions_consumers_connected")
        wait = self.get_time_to_wait(arguments)

        if consumers_connected is not None and consumers_connected < consumers_connected_min:
            if self.needNotify('consumer_conditions', wait):
                self.notifier.send_notification("consumers_connected = %d < %d" % (consumers_connected, consumers_connected_min))
                self.clean('consumer_conditions')
        else:
            self.clean('consumer_conditions')

    def check_connection_conditions(self, arguments):
        response = self.client.get_connections()
        if response is None:
            return

        open_connections = len(response)

        open_connections_min = arguments["generic_conditions"].get("conditions_open_connections")
        wait = self.get_time_to_wait(arguments)

        if open_connections is not None and open_connections < open_connections_min:
            if self.needNotify('open_connections', wait):
                self.notifier.send_notification("open_connections = %d < %d" % (open_connections, open_connections_min))
                self.clean('open_connections')
        else:
            self.clean('open_connections')

    def check_node_conditions(self, arguments):
        response = self.client.get_nodes()
        if response is None:
            return

        nodes_running = len(response)

        conditions = arguments["generic_conditions"]
        nodes_run = conditions.get("conditions_nodes_running")
        node_memory = conditions.get("conditions_node_memory_used")
        wait = self.get_time_to_wait(arguments)


        if nodes_run is not None and nodes_running < nodes_run:
            if self.needNotify('nodes_running', wait):
                self.notifier.send_notification("nodes_running = %d < %d" % (nodes_running, nodes_run))
                self.clean('nodes_running')
        else:
            self.clean('nodes_running')

        for node in response:
            n = 'node_memory_used' + node.get("name")
            if node_memory is not None and node.get("mem_used") > (node_memory * pow(1024, 2)):
                if self.needNotify(n, wait):
                    self.notifier.send_notification("Node %s - node_memory_used = %d > %d MBs" % (node.get("name"), node.get("mem_used"), node_memory))
                    self.clean(n)
            else:
                self.clean(n)


    def get_time_to_wait(self, arguments):
        return arguments['server_time_to_wait'] if 'server_time_to_wait' in arguments else 60

    def needNotify(self, name, wait):

        if wait <= 0:
            return True

        if name not in self.checked:
            # it's first time
            self.checked[name] = time.time() + wait
            return False

        if self.checked[name] < time.time():
            return True

        return False

    def clean(self, name):
        if name in self.checked:
            del self.checked[name]