
import smart_imports

smart_imports.all()


def dijkstra(from_id, to_id, edges):
    n = len(edges)

    distances = [logic.MAX_COST for i in range(n)]
    distances[from_id] = 0

    visited_nodes = [False for i in range(n)]

    previouse_nodes = [None for i in range(n)]

    while True:
        best_cost = logic.MAX_COST + 1
        best_id = None

        for i, visited in enumerate(visited_nodes):
            if visited:
                continue

            if distances[i] < best_cost:
                best_cost = distances[i]
                best_id = i

        if best_id is None:
            break

        for i, distance in enumerate(distances):
            if i == best_id:
                continue

            cost = edges[best_id][i]

            if best_cost + cost < distances[i]:
                distances[i] = best_cost + cost
                previouse_nodes[i] = best_id

        visited_nodes[best_id] = True

    path = []
    node_id = to_id

    while node_id != from_id:
        path.append(node_id)
        node_id = previouse_nodes[node_id]

    path.append(from_id)

    path.reverse()

    return path


def prepair_data(cost_modifiers, paths):
    n = len(cost_modifiers)

    index_to_id = list(cost_modifiers.keys())
    index_to_id.sort()  # fixate order

    id_to_index = {id: i for i, id in enumerate(index_to_id)}

    edges = [[logic.MAX_COST for j in range(n)]
             for i in range(n)]

    for (from_id, to_id), (path, cost) in paths.items():
        # учитываем модификаторы обоих городов, а не только конечного, чтобы сделать более смазанным модификатор пути
        # поскольку если начислять модификатор только на конечный город (что логичнее), то стоимость коротких путей к нему будет
        # слишком уменьаться и терять отличия дргу от друга, что приведёт к частому игнорированию посещения соседних городов
        # (для города с большим бонусом к длинне путей)
        edges[id_to_index[from_id]][id_to_index[to_id]] = max(cost + cost_modifiers[from_id] + cost_modifiers[to_id], c.PATH_MINIMAL_LENGTH)
        # do not reverse path, since its reversed version must be already in paths

    return id_to_index, index_to_id, edges


def search_meta_path(from_id, to_id, cost_modifiers, paths):

    id_to_index, index_to_id, edges = prepair_data(cost_modifiers, paths)

    path = dijkstra(from_id=id_to_index[from_id],
                    to_id=id_to_index[to_id],
                    edges=edges)

    return [index_to_id[i] for i in path]
