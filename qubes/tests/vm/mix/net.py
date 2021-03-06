# pylint: disable=protected-access

#
# The Qubes OS Project, https://www.qubes-os.org/
#
# Copyright (C) 2014-2016  Joanna Rutkowska <joanna@invisiblethingslab.com>
# Copyright (C) 2014-2016  Wojtek Porczyk <woju@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import unittest

import qubes
import qubes.vm.qubesvm

import qubes.tests
import qubes.tests.vm.qubesvm

class TC_00_NetVMMixin(
        qubes.tests.vm.qubesvm.QubesVMTestsMixin, qubes.tests.QubesTestCase):
    def setUp(self):
        super(TC_00_NetVMMixin, self).setUp()
        self.app = qubes.tests.vm.TestApp()
        self.app.vmm.offline_mode = True

    def setup_netvms(self, vm):
        # usage of QubesVM here means that those tests should be after
        # testing properties used here
        self.netvm1 = qubes.vm.qubesvm.QubesVM(self.app, None, qid=2,
            name=qubes.tests.VMPREFIX + 'netvm1',
            provides_network=True)
        self.netvm2 = qubes.vm.qubesvm.QubesVM(self.app, None, qid=3,
            name=qubes.tests.VMPREFIX + 'netvm2',
            provides_network=True)
        self.nonetvm = qubes.vm.qubesvm.QubesVM(self.app, None, qid=4,
            name=qubes.tests.VMPREFIX + 'nonet')
        self.app.domains = qubes.app.VMCollection(self.app)
        for domain in (vm, self.netvm1, self.netvm2, self.nonetvm):
            self.app.domains._dict[domain.qid] = domain
        self.app.default_netvm = self.netvm1
        self.app.default_fw_netvm = self.netvm1


    @qubes.tests.skipUnlessDom0
    def test_140_netvm(self):
        vm = self.get_vm()
        self.setup_netvms(vm)
        self.assertPropertyDefaultValue(vm, 'netvm', self.app.default_netvm)
        self.assertPropertyValue(vm, 'netvm', self.netvm2, self.netvm2,
            self.netvm2.name)
        del vm.netvm
        self.assertPropertyDefaultValue(vm, 'netvm', self.app.default_netvm)
        self.assertPropertyValue(vm, 'netvm', self.netvm2.name, self.netvm2,
            self.netvm2.name)
        self.assertPropertyValue(vm, 'netvm', None, None, '')

    def test_141_netvm_invalid(self):
        vm = self.get_vm()
        self.setup_netvms(vm)
        self.assertPropertyInvalidValue(vm, 'netvm', 'invalid')
        self.assertPropertyInvalidValue(vm, 'netvm', 123)

    def test_142_netvm_netvm(self):
        vm = self.get_vm()
        self.setup_netvms(vm)
        self.assertPropertyInvalidValue(vm, 'netvm', self.nonetvm)

    def test_143_netvm_loopback(self):
        vm = self.get_vm()
        self.app.domains = {1: vm, vm: vm}
        self.assertPropertyInvalidValue(vm, 'netvm', vm)

    def test_150_ip(self):
        vm = self.get_vm()
        self.setup_netvms(vm)
        self.assertPropertyDefaultValue(vm, 'ip', '10.137.0.' + str(vm.qid))
        vm.ip = '192.168.1.1'
        self.assertEqual(vm.ip, '192.168.1.1')

    def test_151_ip_invalid(self):
        vm = self.get_vm()
        self.setup_netvms(vm)
        self.assertPropertyInvalidValue(vm, 'ip', 'abcd')
        self.assertPropertyInvalidValue(vm, 'ip', 'a.b.c.d')
        self.assertPropertyInvalidValue(vm, 'ip', '1111.2222.3333.4444')
        # TODO: implement and add here: 0.0.0.0, 333.333.333.333
