import os
import sys
import unittest
import json

import requests

from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from lib import st2


class BitesizePack(unittest.TestCase):
    def setUp(self):
        host = os.getenv("ST2_ADDRESS")
        key = os.getenv("ST2_APIKEY")

        self.stackstorm = st2.Endpoint(host, key)

        # It's a bit ugly to have assertions here, but we need to validate
        # these.
        params = {
            "key": "bitesize/defaults/jenkinsversion",
            "value": "3.4.35"
        }
        self.assert_success_action("consul.put", params)

        params = {
            "key": "bitesize/defaults/defaultdomain",
            "value": "prsn-dev.io"
        }
        self.assert_success_action("consul.put", params)

    def tearDown(self):
        namespaces = [ 'kubetests-cdt', 'kubetests-jnk', 'kubetests-dev', 'test-app', 'test-app-dev']
        for ns in namespaces:
            params = { "name": ns, "body": {} }
            self.stackstorm.run_action("kubernetes.deleteCoreV1Namespace", params)

        params = { "key": "bitesize/kubetests", "recurse": True }
        self.stackstorm.run_action("consul.delete", params)

    def test_request_ns(self):
        params =  {
            "email": "test@test.com",
            "ns_list": ["dev"],
            "project": "kubetests",
            "gitrepo": "git@github.com:AndyMoore111/test-app-v2.git",
            "gitrequired": True
        }
        self.assert_success_action("bitesize.request_ns", params)

        data = self.assert_success_action("bitesize.list_unapproved_ns", {})
        task_results= data['result']['tasks'][0]['result']['result']
        namespaces = {}
        for t in task_results:
            namespaces.setdefault(t['Key'], t['Value'])

        self.assertIn('bitesize/kubetests/kubetests-dev/unapproved', namespaces.keys())
        self.assertEqual(namespaces['bitesize/kubetests/kubetests-jnk/gitrepo'],'git@github.com:AndyMoore111/test-app-v2.git')

    def test_setup_testapp(self):
        data = self.assert_success_action("bitesize.setup_testapp", {})
        # I'm ashamed to admit that I wrote this. Please do not show this to anyone.
        self.assertEqual(data['result']['tasks'][3]['result']['result']['dep'][0]['metadata']['name'], 'jenkins')

    def test_setup_jenkins(self):
        """ 
        test_setup_jenkins requires kubetests-jnk namespace setup and gitrepo set in consul
        """
        self.helper_create_namespace("kubetests-jnk")

        params  = { 
            "key": "bitesize/kubetests/kubetests-jnk/gitrepo",
            "value": "git@github.com:AndyMoore111/test-app-v2.git"
        }
        self.assert_success_action("consul.put", params)

        params = { "namespace": "kubetests-jnk", "project": "kubetests" }
        self.assert_success_action("bitesize.setup_jenkins", params)

    def test_redis_chain(self):
        """ test_redis_chain NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_redis_status(self):
        """ test_redis_status NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_cassandra_create_chain(self):
        """ test_cassandra_create_chain NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_cassandra_delete_chain(self):
        """ test_cassandra_delete_chain NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_cassandra_status(self):
        """ test_redis_status NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_mongo_create_chain(self):
        """ test_mongo_create_chain NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_mongo_delete_chain(self):
        """ test_mongo_delete_chain NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_mysql_create_chain(self):
        """ test_mysql_create_chain NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_mysql_delete_chain(self):
        """ test_mysql_delete_chain NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_nfs_create_chain(self):
        """ test_nfs_create_chain NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass

    def test_nfs_delete_chain(self):
        """ test_nfs_delete_chain NOT IMPLEMENTED. NEED MOCKS IN ST2 PACKS."""
        pass


    def test_create_ns_vault_rule(self):
        """ test_create_ns_vault_rule NOT IMPLEMENTED. THIS RULE SHOULD BE MOVED OUT OF ST2. """
        # XXX: I don't think we need action like this
        pass








    def test_create_ns(self):
        params = {
            "namespace": "kubetests-cdt",
            "project": "kubetests"
        }
        self.assert_success_action("bitesize.create_ns", params)

    def test_setup_namespace_quota(self):
        self.helper_create_namespace("kubetests-jnk")

        params = {
            "resourcequotas": "10",
            "pods": "5",
            "secrets": "1",
            "namespace": "kubetests-jnk",
            "project": "kubetests"
        }
        self.assert_success_action("bitesize.setup_namespace_quota", params)
        
        params  = { "name": "quota", "namespace": "kubetests-jnk" }
        data = self.assert_success_action("kubernetes.readCoreV1NamespacedResourceQuota", params)
        
        quotas = data['result']['result']['data']['status']
        self.assertEqual(quotas['hard']['resourcequotas'], "10")
        self.assertEqual(quotas['hard']['pods'], "5")
        self.assertEqual(quotas['hard']['secrets'], "1")

        #
        # Now we try to run update and see if it's success. 
        # TODO: This does not work. Seee BITE-1380 for details
        #

        #  params = {
        #      "resourcequotas": "9",
        #      "namespace": "kubetests-jnk",
        #      "project": "kubetests"
        #  }
        #  data = self.assert_success_action("bitesize.setup_namespace_quota", params)
        #  
        #  params  = { "name": "quota", "namespace": "kubetests-jnk" }
        #  data = self.assert_success_action("kubernete.readCoreV1NamespacedResourceQuota", params)

        #  quotas = data['result']['result']['data']['status']
        #  self.assertEqual(quotas['hard']['resourcequotas'], "9")
        #  self.assertEqual(quotas['hard']['pods'], "5")
        #  self.assertEqual(quotas['hard']['secrets'], "1")

    def test_setup_namespace_secret(self):
        pass


    def test_create_project(self):
        params = { "project": "kubetests" }
        self.assert_success_action("bitesize.create_project", params)

    def assert_success_action(self, action, params):
        success, data = self.stackstorm.run_action(action, params)
        self.assertTrue(
            success,
            "{} failed.\n\tData: {}\n\tParams: {}\n".format(
                action,
                json.dumps(data),
                json.dumps(params)
            )
        )
        return data

    def helper_create_namespace(self, namespace):
        params = { 
            "body": {
                "kind": "Namespace",
                "apiVersion": "v1",
                "metadata": {
                    "labels": {"project": "kubetests"},
                    "name": namespace
                }
            }
        }
        self.stackstorm.run_action("kubernetes.createCoreV1Namespace", params)


if __name__ == "__main__":
    unittest.main(verbosity=2)
