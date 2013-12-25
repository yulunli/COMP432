from network_model import Network, Node, Utils
import random


class Simulation():
    testDim = (100, 100)
    num_messages = 500
    max_attempts = 500

    def runSimulation(self, sim_type=0):
        types = ["kleinberg", "yule"]
        testNetwork = Network(self.testDim, network_type=types[sim_type])
        testWorld = testNetwork.world
        nodeIdTuple = tuple([key for key in testNetwork.world.keys() if testNetwork.world[key].has_user])
        lengths = []
        all_traces = []
        num_failed = 0
        if len(nodeIdTuple) > 2:
            for j in range(self.num_messages):
                testNodes = random.sample(nodeIdTuple, 2)
                testNode = testNodes[0]
                testNode1 = testNodes[1]
                distance = -1
                i = 0
                trace = [[i, testWorld[testNode].position,
                          testNetwork.getDistance(testWorld[testNode].position, testWorld[testNode1].position),
                          testNode]]
                while distance != 0:
                    i += 1
                    testNeighborsHash = list(testWorld[testNode].out_links)
                    distances = []
                    for neighbor in testNeighborsHash:
                        distance = testNetwork.getDistance(testWorld[testNode1].position, testWorld[neighbor].position)
                        distances.append(distance)
                    minNeighborIndex = distances.index(min(distances))
                    minNeighborHash = testNeighborsHash[minNeighborIndex]
                    trace.append([i, testWorld[minNeighborHash].position, min(distances), minNeighborHash])
                    if min(distances) == 0:
                        lengths.append(i)
                        # print(str(i) + ' Done!')
                        break
                    elif i == self.max_attempts:
                        num_failed += 1
                        break
                    else:
                        testNode = minNeighborHash
                        distance = min(distances)
                all_traces.append(trace)
            print(1.0 * sum(lengths) / len(lengths), Utils.median(lengths), 1 - 1.0 * num_failed / self.num_messages)
            return all_traces

    def main(self):
        self.runSimulation()
        # self.runSimulation(1)


if __name__ == "__main__":
    s = Simulation()
    s.main()
    # nw = Network([10, 10], "yule")
    # for nodeId in nw.world:
    #     print(nw.get_position(nodeId))
    #     print(len([nw.get_position(neighbor) for neighbor in nw.world[nodeId].neighborsHash]))
    # print([nw.get_position(in_link) for in_link in nw.world[nodeId].in_links])