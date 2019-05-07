
import smart_imports

smart_imports.all()


M = logic.MAX_COST


class DijkstraTests(utils_testcase.TestCase):

    def test_single_node(self):
        path = waypoints.dijkstra(from_id=0, to_id=0, edges=[[M]])
        self.assertEqual(path, [0])

    def test_minimum_nodes(self):
        path = waypoints.dijkstra(from_id=1, to_id=0, edges=[[M, 1],
                                                             [1, M]])
        self.assertEqual(path, [1, 0])

    def test_not_used_node(self):
        # 0 - start
        # 1 - missed
        # 2 - end
        # 3 - middle node
        path = waypoints.dijkstra(from_id=0, to_id=2, edges=[[M, 2, 3, 1],
                                                             [2, M, 2, M],
                                                             [3, 2, M, 1],
                                                             [1, M, 1, M]])
        self.assertEqual(path, [0, 3, 2])

        # 0 - start
        # 1 - middle node
        # 2 - end
        # 3 - missed

        path = waypoints.dijkstra(from_id=0, to_id=2, edges=[[M, 0, 3, 4],
                                                             [2, M, 2, M],
                                                             [3, 2, M, 4],
                                                             [4, M, 4, M]])
        self.assertEqual(path, [0, 1, 2])

    def test_complex_path(self):
        # 0 - start
        # 1 - missed
        # 2 - end
        # 3 - middle node 2
        # 4 - middle node 1

        edges = [[M, M, M, M, 1],
                 [M, M, M, M, M],
                 [M, M, M, 1, M],
                 [M, M, 1, M, 1],
                 [1, M, M, 1, M]]

        for i in range(5):
            for j in range(5):
                if edges[i][j] == M:
                    edges[i][j] = random.randint(5, 100)

        path = waypoints.dijkstra(from_id=0, to_id=2, edges=edges)
        self.assertEqual(path, [0, 4, 3, 2])

        # 0 - start
        # 1 - missed
        # 2 - end
        # 3 - middle node 1
        # 4 - middle node 2

        edges = [[M, M, M, 1, M],
                 [M, M, M, M, M],
                 [M, M, M, M, 1],
                 [1, M, M, M, 1],
                 [M, M, 1, 1, M]]

        for i in range(5):
            for j in range(5):
                if edges[i][j] == M:
                    edges[i][j] = random.randint(5, 100)

        path = waypoints.dijkstra(from_id=0, to_id=2, edges=edges)
        self.assertEqual(path, [0, 3, 4, 2])

    def test_real_performance(self):
        n = 100

        edges = [[random.randint(1, 1000) for j in range(n)]
                 for i in range(n)]

        path = waypoints.dijkstra(from_id=0, to_id=1, edges=edges)

        self.assertTrue(path)


class PrepairDataTests(utils_testcase.TestCase):

    def test_no_nodes(self):
        id_to_index, index_to_id, edges = waypoints.prepair_data(cost_modifiers={}, paths={})

        self.assertEqual(id_to_index, {})
        self.assertEqual(index_to_id, [])
        self.assertEqual(edges, [])

    def test_sinle_node(self):
        id_to_index, index_to_id, edges = waypoints.prepair_data(cost_modifiers={3: 10},
                                                                 paths={})

        self.assertEqual(id_to_index, {3: 0})
        self.assertEqual(index_to_id, [3])
        self.assertEqual(edges, [[M]])

    def test_simples_paths(self):
        id_to_index, index_to_id, edges = waypoints.prepair_data(cost_modifiers={3: 10,
                                                                                 5: 100},
                                                                 paths={(3, 5): (None, 101),
                                                                        (5, 3): (None, 102)})

        self.assertEqual(id_to_index, {3: 0, 5: 1})
        self.assertEqual(index_to_id, [3, 5])
        self.assertEqual(edges, [[M, 211],
                                 [212, M]])

    def test_complex_paths(self):
        id_to_index, index_to_id, edges = waypoints.prepair_data(cost_modifiers={3: 10,
                                                                                 5: 100,
                                                                                 13: 1000},
                                                                 paths={(3, 5): (None, 101),
                                                                        (5, 3): (None, 102),
                                                                        (5, 13): (None, 103),
                                                                        (13, 5): (None, 104)})

        self.assertEqual(id_to_index, {3: 0, 5: 1, 13: 2})
        self.assertEqual(index_to_id, [3, 5, 13])
        self.assertEqual(edges, [[M, 211, M],
                                 [212, M, 1203],
                                 [M, 1204, M]])


class SearchMetaPathTests(utils_testcase.TestCase):

    def test_signle_node(self):
        path = waypoints.search_meta_path(from_id=3,
                                          to_id=3,
                                          cost_modifiers={3: 10},
                                          paths={})
        self.assertEqual(path, [3])

    def test_simple_path(self):
        path = waypoints.search_meta_path(from_id=3,
                                          to_id=5,
                                          cost_modifiers={3: 10,
                                                          5: 100},
                                          paths={(3, 5): (None, 101),
                                                 (5, 3): (None, 102)})
        self.assertEqual(path, [3, 5])

    def test_complex_path(self):
        paths = {(3, 5): (None, 101),
                 (5, 3): (None, 102),
                 (5, 13): (None, 103),
                 (13, 5): (None, 104)}

        costs = {3: 10,
                 5: 100,
                 13: 1000}

        path = waypoints.search_meta_path(from_id=3,
                                          to_id=13,
                                          cost_modifiers=costs,
                                          paths=paths)
        self.assertEqual(path, [3, 5, 13])

        path = waypoints.search_meta_path(from_id=13,
                                          to_id=3,
                                          cost_modifiers=costs,
                                          paths=paths)
        self.assertEqual(path, [13, 5, 3])
