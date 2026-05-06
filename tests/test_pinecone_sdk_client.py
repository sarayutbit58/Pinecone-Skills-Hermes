import sys
import types
import unittest


class FailingIndex:
    def query(self, **kwargs):
        raise ValueError("network failed")

    def upsert(self, **kwargs):
        raise ValueError("network failed")


class FakePinecone:
    def __init__(self, api_key):
        self.api_key = api_key

    def Index(self, index_name):
        return FailingIndex()


class PineconeSdkClientTests(unittest.TestCase):
    def setUp(self):
        fake_module = types.ModuleType("pinecone")
        fake_module.Pinecone = FakePinecone
        sys.modules["pinecone"] = fake_module
        sys.modules.pop("src.pinecone_sdk_client", None)

    def test_query_and_upsert_wrap_pinecone_errors(self):
        from src.config import load_config
        from src.pinecone_sdk_client import PineconeSdkClient

        client = PineconeSdkClient(load_config({"pinecone": {"index_name": "test-index"}}))

        with self.assertRaisesRegex(RuntimeError, "Pinecone query failed for index 'test-index'"):
            client.query(vector=[0.1], top_k=1)
        with self.assertRaisesRegex(RuntimeError, "Pinecone upsert failed for index 'test-index'"):
            client.upsert([])


if __name__ == "__main__":
    unittest.main()
