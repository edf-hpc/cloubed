#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Rémi Palancher 
#
# This file is part of Cloubed.
#
# Cloubed is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Cloubed is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Cloubed.  If not, see
# <http://www.gnu.org/licenses/>.

""" EventManager class of Cloubed """

import threading
import libvirt
import logging
from Domain import Domain
from DomainEvent import DomainEvent

class EventManager:

    """ EventManager class """

    def __init__(self):

        libvirt.virEventRegisterDefaultImpl()

        self._thread = threading.Thread(target=EventManager.run_event_loop,
                                        name="libvirtEventLoop")
        self._thread.setDaemon(True)
        self._thread.start()

        self._conn = libvirt.openReadOnly('qemu:///system')
        self._conn.domainEventRegister(EventManager.manage_event, None)
        self._conn.setKeepAlive(5, 3)

        logging.debug("initialized event manager")

    @staticmethod
    def run_event_loop():

        """ run_event_loop: Starts libvirt event loop """

        while True:
            libvirt.virEventRunDefaultImpl()

    @staticmethod
    def manage_event(conn, dom, event_type, event_detail, opaque):

        """ manage_event: handler launched by libvirt in case of event """

        event = DomainEvent(event_type, event_detail)
        logging.debug("event on domain {domain_name}({domain_id}) " \
                      "{event_type} {event_detail}" \
                          .format(domain_name=dom.name(),
                                  domain_id=dom.ID(),
                                  event_type=event.get_type(),
                                  event_detail=event.get_detail()))
        domain = Domain.get_by_name(dom.name())
        domain.notify_event(event)

