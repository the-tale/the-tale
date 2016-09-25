# coding: utf-8
import copy

class Node(object):

    __slots__ = ('uid', 'data', 'children')

    def __init__(self, uid, data=None, children=None):
        self.data = data
        self.uid = uid
        self.children = {} if children is None else dict(children)

    def add_path(self, path):
        if not path:
            return

        node = path[0]

        if node.uid not in self.children:
            self.children[node.uid] = node
        else:
            self.children[node.uid].merge(node)

        self.children[node.uid].add_path(path[1:])

    def merge(self, other):
        raise NotImplementedError()

    def label(self):
        raise NotImplementedError()


    def process_depth_first(self, processor):
        for child in self.children.itervalues():
            child.process_depth_first(processor)
        processor(self)


    def random_path(self, randomizer):
        next_node = randomizer(self)

        if next_node is None:
            return [self]

        return [self] + next_node.random_path(randomizer)


    def filter(self, predicate):

        if not predicate(self):
            return None

        node = self.__class__(uid=self.uid, data=copy.deepcopy(self.data))

        for child in self.children.itervalues():
            child_node = child.filter(predicate)
            if child_node is None:
                continue
            node.children[child_node.uid] = child_node

        return node

    def serialize(self):
        return {'uid': self.uid,
                'data': self.data,
                'children': {uid: child.serialize() for uid, child in self.children.iteritems()}}

    @classmethod
    def deserialize(cls, data):
        return cls(uid=data['uid'],
                   data=data['data'],
                   children={uid: cls.deserialize(child) for uid, child in data['children'].iteritems()})



class Drawer(object):

    def __init__(self, tree):
        import gv
        self.gv = gv
        self.tree = tree
        self.graph = gv.strictdigraph('tree')
        self.nodes = {}

    def draw(self, path):
        self.draw_tree_node(self.tree)

        self.gv.layout(self.graph, 'dot');
        self.gv.render(self.graph, path[path.rfind('.')+1:], path)


    def draw_tree_node(self, node):

        self.add_node(node)

        for child in node.children.values():
            self.draw_tree_node(child)
            self.add_edge(node, child)


    def add_node(self, tree_node):
        node = self.gv.node(self.graph, tree_node.uid.encode('utf-8'))
        self.gv.setv(node, 'shape', 'plaintext')
        self.gv.setv(node, 'label', self.create_label_for(tree_node).encode('utf-8'))
        self.gv.setv(node, 'fontsize', '10')

        self.nodes[tree_node.uid] = node

        return node


    def add_edge(self, parent, child):
        edge = self.gv.edge(self.nodes[parent.uid], self.nodes[child.uid])

        # self.gv.setv(edge, 'dir', 'none')
        self.gv.setv(edge, 'weight', '40')
        self.gv.setv(edge, 'minlen', '1')

        return edge


    def create_label_for(self, tree_node):
        trs = []

        # trs.append(tr(td(i(tree_node.uid))))

        bgcolor = '#aaffaa'

        trs.append(tr(td(tree_node.label())))

        return table(*trs,
                     bgcolor=bgcolor,
                     port=tree_node.uid)


def b(data): return u'<b>%s</b>' % data
def i(data): return u'<i>%s</i>' % data

def table(*trs, **kwargs):
    bgcolor = kwargs.get('bgcolor')
    port = kwargs.get('port')
    border = kwargs.get('border', 1)
    return u'''<
    <table cellpadding="1"
           cellspacing="0"
           border="%(border)d"
           %(bgcolor)s
           %(port)s
           cellborder="1">%(body)s</table>
    >''' % {'body': ''.join(trs),
            'border': border,
            'port': 'port="%s"' % port if port else '',
            'bgcolor': 'BGCOLOR="%s"' % bgcolor if bgcolor is not None else ''}

def tr(*tds):
    return u'<tr BGCOLOR="#00ff00">%s</tr>' % ''.join(tds)

def td(body, port=None, **kwargs):
    bgcolor = kwargs.get('bgcolor')
    colspan = kwargs.get('colspan', 1)
    align = kwargs.get('align', 'left')
    border = kwargs.get('border', 0)
    return u'''<td
                 %(port)s
                 COLSPAN="%(colspan)d"
                 border="%(border)d"
                 align="%(align)s"
                 %(bgcolor)s>%(body)s</td>''' % {'body': body,
                                                 'colspan': colspan,
                                                 'align': align,
                                                 'border': border,
                                                 'port': 'port="%s"' % port if port else '',
                                                 'bgcolor': 'BGCOLOR="%s"' % bgcolor if bgcolor is not None else '' }
