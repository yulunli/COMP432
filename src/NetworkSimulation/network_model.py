from collections import defaultdict
from copy import deepcopy
import cPickle
import datetime
import operator
import os
import random
import sys
import time


class Dim():
    """
    A dimension object has dimensions in tuple, list of diameter in each dimension.
    diam is the diameter of the network, which is the shortest longest distance.
    """

    def __init__(self, network_dimension):
        """
        @param network_dimension: tuple
        """
        self.dimensions = network_dimension
        self.diameters = [size / 2 for size in network_dimension]
        self.diam = sum(self.diameters)


class Node():
    """
    A node is the basic unit of the network.
    """

    def __init__(self, position, dim, exclude_distance=1):
        """
        @param position: tuple
        @param dim: Dim
        """
        self.position = position
        self.dim = dim
        self.neighborhood_radius = exclude_distance
        self.id = hash(position)  # unique identifier of the node
        self.has_user = True
        self.out_links = set(
            [hash(tuple(neighbor)) for neighbor in self.getNeighborByDistance(self.neighborhood_radius)])
        self.in_links = deepcopy(self.out_links)  # nodes with l1 distance of 1 have mutual connection

    def move(self, position, moveOnDim, distance):
        """
        Change the position of a node.
        @param position: tuple
        """
        position[moveOnDim] = (position[moveOnDim] + distance) % self.dim.dimensions[moveOnDim]

    def getNeighborByDistance(self, n):
        """
        Return the positions of the neighbors (l1 distance of n)
        """
        neighbors = set()
        for i in range(n):
            tempMovements = (i, n - i), (-i, n - i), (i, -(n - i)), (-i, -(n - i)), \
                            (n - i, i), (n - i, -i), (-(n - i), i), (-(n - i), -i)
            movements = set()
            for tempMovement in tempMovements:
                qualified = True
                for i in range(len(self.dim.dimensions)):
                    if abs(tempMovement[i]) > self.dim.diameters[i]:
                        qualified = False
                        break
                if qualified:
                    movements.add(tempMovement)
            for movement in movements:
                tempPosition = list(self.position)
                for j in range(len(self.dim.dimensions)):
                    self.move(tempPosition, j, movement[j])
                neighbors.add(tuple(tempPosition))
        return neighbors


class Network():
    """
    Generate a network of Node objects.
    """

    def __init__(self, worldDimension, density=0.6, network_type="kleinberg", num_out_links=1, pickles_dir="pickles/",
                 neighborhood_radius=1, real_connection=True):
        """
        Default network_type is kleinberg, which ignors preferential attachment.
        Generated models of diameter greater than 25 are picked to pickles/*
        @param worldDimension: tuple
        @param real_connection: bool True if every out-link is also an in-link
        """
        self.network_type = network_type
        self.dim = Dim(worldDimension)
        self.density = density
        self.num_out_links = num_out_links
        self.neighborhood_radius = neighborhood_radius
        self.num_nodes = reduce(operator.mul, self.dim.dimensions, 1)
        self.basic_network = self.get_basic_network()
        self.basic_network_nodes = self.basic_network.keys()
        self.real_connection = real_connection
        self.pickle_file_name = pickles_dir + self.get_pickle_file_name(self.dim.dimensions,
                                                                        [self.density, network_type, num_out_links]) + ".pickled"
        if Utils.has_cached_file(self.pickle_file_name):
            self.world = Utils.read_from_cache(self.pickle_file_name)
        else:
            self.world = getattr(self, "get_" + network_type + "_network")()
            if self.dim.diam > 25:
                Utils.write_to_cache(pickles_dir, self.pickle_file_name, self.world)

    def get_pickle_file_name(self, dimensions, *args):
        """
        Helper method, get the name for the model for pickled file name
        @param dimensions: list|tuple
        """
        file_name_helper = [str(dimension) for dimension in dimensions]
        file_name_helper.extend(*args)
        return "_".join([str(helper) for helper in file_name_helper])

    def get_basic_network(self):
        """
        Set up the basic network of the right size and each node is connected to nodes of l1 distance 1.
        """
        tempWorld = []
        for i in range(self.dim.dimensions[0]):
            tempWorld.append([i])
        for i in range(len(self.dim.dimensions) - 1):
            cWorld1 = []
            for j in range(self.dim.dimensions[i + 1]):
                cWorld = [list(world) for world in tempWorld]
                for node in cWorld:
                    node.append(j)
                cWorld1.extend(cWorld)
            tempWorld = [list(world) for world in cWorld1]
        testWorld = {}
        for position in tempWorld:
            node = Node(tuple(position), self.dim)
            testWorld[node.id] = node
        for node_id in testWorld:
            test = random.random()
            if test > self.density:
                testWorld[node_id].has_user = False
                for out_link in testWorld[node_id].out_links:
                    testWorld[out_link].in_links.remove(node_id)
                    testWorld[out_link].out_links.remove(node_id)
                testWorld[node_id].in_links = set()
                testWorld[node_id].out_links = set()
        print("Basic network done! ({0} = {1} nodes)".format(" x ".join([str(item) for item in self.dim.dimensions]),
                                                             self.num_nodes))
        return testWorld

    def get_kleinberg_network(self, far_connection=1):
        """
        Return a network generated using the Kleinberg paper.
        """
        network = self.basic_network
        progress_meter = Utils.ProgressMeter(self.num_nodes)
        for i in range(far_connection):
            for nodeId in network:
                if network[nodeId].has_user:
                    new_connection = self.get_kleinberg_connection(network[nodeId])
                    connection_hash = hash(new_connection)
                    network[nodeId].out_links.add(connection_hash)
                    network[connection_hash].in_links.add(nodeId)
                    if self.real_connection:
                        network[nodeId].in_links.add(connection_hash)
                        network[connection_hash].out_links.add(nodeId)
                progress_meter.show_progress()
        print("Finished building " + self.network_type + " network!")
        return network

    def get_kleinberg_connection(self, node, cluster_exponent=1):
        """
        Return the position of a generated Kleinberg connection.
        @param node: Node
        """
        helper = defaultdict(set)
        for node_id, test_node in self.basic_network.iteritems():
            if test_node.has_user:
                temp_distance = self.getDistance(node.position, test_node.position)
                if temp_distance > self.neighborhood_radius:
                    helper[temp_distance].add(node_id)
        bin_helper = [(distance, len(connections)) for distance, connections in helper.iteritems()]
        raw_bin = [1.0 * num_users / (distance ** cluster_exponent) for distance, num_users in bin_helper]
        bin_num = Utils.select_bin(raw_bin)
        candidates = helper[bin_helper[bin_num][0]]
        return random.sample(candidates, 1)[0]

    def get_yule_network(self):
        """
        Return a network that considers preferential attachment.
        """
        network = self.basic_network
        helper = defaultdict(set)
        for node_id in network:
            if network[node_id].has_user:
                helper[len(network[node_id].in_links)].add(node_id)
        node_ids = [n_id for n_id in network if network[n_id].has_user]
        assignedNodes = set()
        for i in range(self.num_out_links):
            progress_meter = Utils.ProgressMeter(self.num_nodes)
            for node_id in node_ids:
                if node_id not in assignedNodes:
                    connection_id = self.get_yule_connection(network[node_id], helper)
                    for key in helper:
                        if connection_id in helper[key]:
                            helper[key].remove(connection_id)
                    network[node_id].out_links.add(connection_id)
                    network[connection_id].in_links.add(node_id)
                    if self.real_connection:
                        network[node_id].in_links.add(connection_id)
                        network[connection_id].out_links.add(node_id)
                    assignedNodes.add(node_id)
                    helper[len(network[connection_id].in_links)].add(connection_id)
                    progress_meter.show_progress()
            print("Finished building " + self.network_type + " network!")
        return network

    def get_yule_connection(self, node, helper):
        """
        Return a connection that considers preferential attachment.
        @param node: Node
        @param helper: dict
        """
        exclude_list = [node.id]
        exclude_list.extend(node.out_links)
        count_in_links = sorted(helper.keys())
        raw_bin = [len(helper[count_in_links[i]]) * (count_in_links[i] ** 2) for i in range(len(count_in_links))]
        connection_id = node.id
        while connection_id == node.id:
            from_bin = Utils.select_bin(raw_bin)
            candidate = random.sample(helper[count_in_links[from_bin]], 1)[0]
            if candidate not in exclude_list:
                connection_id = candidate
        return connection_id

    def get_position(self, nodeId):
        return self.world[nodeId].position

    def getDistance(self, position1, position2):
        total = 0
        for i in range(len(position1)):
            diff = abs(position1[i] - position2[i])
            total += diff if 2 * diff <= self.dim.dimensions[i] else self.dim.dimensions[i] - diff
        return total

    def get_random_connection(self, node):
        """
        Return the id of a random connection in the network.
        """
        exclude_list = [node.id]
        exclude_list.extend(node.out_links)
        candidates = random.sample(self.basic_network_nodes, len(exclude_list) + 1)
        for candidate in candidates:
            if candidate not in exclude_list:
                return candidate


class Utils():
    @staticmethod
    def median(unsortedList):
        """
        Return the median.
        @param unsortedList: list
        """
        sorts = sorted(unsortedList)
        length = len(sorts)
        if not length % 2:
            return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
        return sorts[length / 2]

    @staticmethod
    def select_bin(raw_bin):
        """
        Randomly select a bin given a raw_bin with a list of bin width.
        """
        normalized_bin = [(1.0 * width) / sum(raw_bin) for width in raw_bin]
        # print(normalized_bin)
        tracker = normalized_bin[0]
        select_helper = random.random()
        for i in range(len(normalized_bin)):
            if select_helper < tracker:
                return i
            elif i < len(normalized_bin) - 1:
                tracker += normalized_bin[i + 1]
            else:
                return i

    @staticmethod
    def has_cached_file(pickle_file_name):
        return os.path.isfile(pickle_file_name)

    @staticmethod
    def read_from_cache(pickle_file_name):
        with open(pickle_file_name, 'r') as f:
            obj = cPickle.load(f)
        return obj

    @staticmethod
    def write_to_cache(pickles_dir, pickle_file_name, obj):
        if not os.path.exists(pickles_dir):
            os.makedirs(pickles_dir)
        with open(pickle_file_name, 'w') as f:
            cPickle.dump(obj, f)

    class ProgressMeter():
        """
        Utility class to show the progress of the program.
        """

        def __init__(self, num_work, checkpoint=1000):
            """
            @param num_work: int size of the overall loop
            """
            self.num_work = num_work
            self.checkpoint = checkpoint
            self.increment = int(1.0 * self.num_work / checkpoint) if 1.0 * self.num_work / checkpoint > 1 else 1
            self.counter = 0
            self.timer = time.time()

        def show_progress(self):
            """
            Updates progress when called.
            """
            if self.counter % self.increment == 0:
                speed = self.counter / (time.time() - self.timer) if self.counter != 0 else 0
                remaining_time_string = str(
                    datetime.timedelta(
                        seconds=int((self.num_work - self.counter) / speed))) if self.counter != 0 else "???"

                sys.stdout.write("{0:3d} % completed ({1:.1f} nodes/sec) Estimated time to finish: {2}\r".format(
                    int(100.0 * self.counter / self.num_work), speed, remaining_time_string))
            self.counter += 1