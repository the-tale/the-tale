# coding: utf-8

import random
import datetime
import collections

from the_tale.common.utils import simple_tree

from the_tale.accounts.models import Account#, RandomPremiumRequest

from the_tale.bank.models import Invoice

from django.core.management.base import BaseCommand

# chests_query = RandomPremiumRequest.objects.filter(receiver__in=ids, created_at__gt=datetime.datetime.now() - datetime.timedelta(days=30))
# print 'from chests: ', chests_query.count()


def get_premium_sequences(accounts_query):
    ids = accounts_query.values_list('id', flat=True)

    invoices_query = Invoice.objects.filter(recipient_id__in=ids, operation_uid__contains='subscription')

    operations = invoices_query.order_by('created_at').values_list('recipient_id', 'operation_uid')

    operations_by_accounts = {}

    for account_id, operation_uid in operations:
        if account_id not in operations_by_accounts:
            operations_by_accounts[account_id] = []
        operations_by_accounts[account_id].append(operation_uid)

    operations_by_accounts = {account_id: tuple(normalize(operations)) for account_id, operations in operations_by_accounts.iteritems()}

    return collections.Counter(operations_by_accounts.itervalues())


def normalize(ops):
    result = []
    for op in ops:
        for x in (7, 15, 30, 90):
            if str(x) in op:
                result.append(x)
                continue
    return result


def print_sequences(sequences):
    for operations, count in sorted(sequences.items(), key=lambda x: x[1]):
        print 'count: %3d total: %3d seq: %r' % (count, sum(operations), operations)


class StatsNode(simple_tree.Node):

    def merge(self, other):
        self.data['total_stop'] += other.data['total_stop']
        self.data['active_stop'] += other.data['active_stop']


    @property
    def active_stop(self): return self.data['active_stop']

    @property
    def total_stop(self): return self.data['total_stop']

    @property
    def active_next(self): return self.data['active_next']

    @property
    def total_next(self): return self.data['total_next']

    @property
    def conversion_passed(self): return self.total_next

    @property
    def conversion_total(self): return self.total_stop + self.total_next - self.active_stop

    @property
    def conversion_percents(self): return float(self.conversion_passed) / self.conversion_total if self.conversion_total else 0

    def label(self):

        label = u'''
<font point-size="14pt">%s</font> <br/>
остановившиеся: <br/>
%d [акт %d ~ %.2f] <br/>
прошедшие: <br/>
 %d  [акт %d ~ %.2f] <br/>
конверсия:<br/>
%d / %d ~ %.2f'''

        return label % (self.data['uid'],
                        self.total_stop,
                        self.active_stop,
                        float(self.active_stop) / self.total_stop if self.total_stop else 0,
                        self.total_next,
                        self.active_next,
                        float(self.active_next) / self.total_next if self.total_next else 0,
                        self.conversion_passed,
                        self.conversion_total,
                        self.conversion_percents)


class Command(BaseCommand):

    help = 'dump all dymamic portal data and send to email from settings.DUMP_EMAIL'

    requires_model_validation = False

    def handle(self, *args, **options):

        old_premiums_now_active = get_premium_sequences(Account.objects.filter(is_fast=False,
                                                                               premium_end_at__lt=datetime.datetime.now(),
                                                                               active_end_at__gt=datetime.datetime.now()))
        print 'old_premiums now active: ', sum(old_premiums_now_active.itervalues())

        # print '-----PREMIUMS----'
        premiums = get_premium_sequences(Account.objects.filter(is_fast=False, premium_end_at__gt=datetime.datetime.now()))
        # print_sequences(premiums)

        # print
        # print '-----ALL---------'
        alls = get_premium_sequences(Account.objects.filter(is_fast=False))
        # print_sequences(alls)

        # print
        # print '-----OLD---------'
        # olds = alls - premiums
        # print_sequences(olds)


        tree = StatsNode(uid='root', data={'uid': u'root',
                                           'len': 0,
                                           'total_stop': 0,
                                           'active_stop': 0})

        for path, count in alls.iteritems():
            # if count == 1:
            #     continue

            tree_path = [tree]
            for length in path:
                tree_path.append(StatsNode(uid=u'%s_%d' % (tree_path[-1].uid, length),
                                           data={'uid': u'%s' % length,
                                                 'len': length,
                                                 'total_stop': 0,
                                                 'active_stop': 0}))
            tree_path[-1].data['total_stop'] = count
            tree.add_path(tree_path[1:])

        for path, count in premiums.iteritems():
            # if count == 1:
            #     continue

            tree_path = [tree]
            for length in path:
                tree_path.append(StatsNode(uid=u'%s_%d' % (tree_path[-1].uid, length),
                                           data={'uid': u'%s' % length,
                                                 'len': length,
                                                 'total_stop': 0,
                                                 'active_stop': 0}))
            tree_path[-1].data['active_stop'] = count
            tree.add_path(tree_path[1:])

        def processor(node):
            node.data['active_next'] = sum(child.data['active_next'] + child.data['active_stop'] for child in node.children.itervalues())
            node.data['total_next'] = sum(child.data['total_next'] + child.data['total_stop'] for child in node.children.itervalues())

        tree.process_depth_first(processor)


        def randomizer(node):
            if random.uniform(0, 1) > node.conversion_percents:
                return None

            if not node.children:
                return None

            total = sum(child.conversion_total for child in node.children.itervalues())
            choice_value = random.randint(0, total)

            for child in node.children.itervalues():
                if choice_value <= child.conversion_total:
                    return child
                choice_value -= child.conversion_total


        N = 100000
        lens = sorted(collections.Counter(sum(node.data['len'] for node in tree.random_path(randomizer)) for i in xrange(N)).items(),
                      key=lambda x: x[1])

        # for length, count in lens:
        #     print '%4d %d' % (length, count)

        def print_gt(barier):
            print '> %d: %.2f ~ (>%.2f$)' % (barier, sum(float(count) / N for length, count in lens if length > barier), 7.5 * barier / 90)

        print
        MEDIUM = sum(length * float(count) / N for length, count in lens)
        print 'medium: ', MEDIUM
        print_gt(30)
        print_gt(60)
        print_gt(90)
        print_gt(180)
        print_gt(360)

        ids = Account.objects.filter(is_fast=False, created_at__gt=datetime.datetime.now() - datetime.timedelta(days=MEDIUM)).values_list('id', flat=True)
        prems_for_medium_days = len(set(Invoice.objects.filter(recipient_id__in=ids, operation_uid__contains='subscription').values_list('recipient_id')))
        print 'prems for medium days:', prems_for_medium_days
        print 'to acquire in day > %.2f ' % (prems_for_medium_days / MEDIUM)

        for i in xrange(10):
            tree = tree.filter(lambda node: node.data['total_stop'] > 1 or node.children)

        simple_tree.Drawer(tree).draw('/tmp/tree.png')
