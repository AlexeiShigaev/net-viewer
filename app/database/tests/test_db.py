import pprint
import unittest

from app.database.mongo_motor import MongoMotorEngine


async def count(cursor):
    i = 0
    async for _ in cursor:
        i += 1
    return i

static_data1 = {"user": "admin", "hash": "wslwsflb123svlwfb"}
static_data2 = {"user": "abc", "hash": "ddd"}


class TestDB(unittest.IsolatedAsyncioTestCase):
    async def test_all(self):
        motor = MongoMotorEngine(
            connection_uri="mongodb://mongoadmin:GhjcnjGfhjkm12@localhost:27017",
            database="macfinder"
        )
        await motor.drop_collection("test")
        res = await motor.insert_one(
            collection="test",
            document=static_data1
        )
        self.assertIsNotNone(res)
        res = await motor.insert_one(
            collection="test",
            document=static_data2
        )
        self.assertIsNotNone(res)

        res = motor.find(
            "test",
            {"user": "abc"}
        )
        res_list = await res.to_list(None)
        print("find result: {}".format(res_list))
        self.assertEqual(len(res_list), 1)

        one = await motor.find_one(
            "test",
            {"user": "abc"}
        )
        print("find_one: {}".format(one))
        self.assertEqual(len(one), 3)


if __name__ == '__main__':
    unittest.main()
