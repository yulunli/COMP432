import unittest

from network_model import Node, Network, Dim


class TestNode(unittest.TestCase):
    def setUp(self):
        self.testNodePosition = (3, 3)
        self.dimensions = (5, 5)
        self.testNode = Node(self.testNodePosition, Dim(self.dimensions))
        self.testDistance = 5

        # self.testWorld = Network(self.dimensions)

    @unittest.skip
    def test_Network(self):
        for nodeId in self.testWorld.world:
            # print(self.testWorld.world[nodeId].position, [self.testWorld.world[ol].position for ol in self.testWorld.world[nodeId].out_links])
            for out_link in self.testWorld.world[nodeId].out_links:
                self.assertIn(out_link, self.testWorld.world)

    def test_yule_network(self):
        nw = Network([5, 5], network_type="kleinberg")
        for nodeId in nw.world:
            print(nw.world[nodeId].position, nw.world[nodeId].has_user, [nw.world[ol].position for ol in nw.world[nodeId].in_links])
            # print(nw.world[nodeId].position, nw.world[nodeId].has_user, [nw.world[ol].position for ol in nw.world[nodeId].out_links])
            # print([nw.get_position(in_link) for in_link in nw.world[nodeId].in_links])


if __name__ == '__main__':
    pickles_dir = "pickles/"
    unittest.main()