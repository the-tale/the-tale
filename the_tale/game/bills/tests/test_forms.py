# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.bills import forms
from the_tale.game.bills import relations


class BaseUserFormTests(testcase.TestCase):

    def setUp(self):
        pass


    def test_no_duration(self):
        form = forms.BaseUserForm({'caption': 'bill-caption',
                                  'rationale': 'bill-rationale',
                                  'chronicle_on_accepted': 'chronicle-on-accepted'})

        self.assertTrue(form.is_valid())


    def test_no_duration__chronicle_on_ended(self):
        form = forms.BaseUserForm({'caption': 'bill-caption',
                                  'rationale': 'bill-rationale',
                                  'chronicle_on_accepted': 'chronicle-on-accepted',
                                  'chronicle_on_ended': 'chronicle-on-ended'})

        self.assertFalse(form.is_valid())


    def test_duration__no_chronicle_on_ended(self):
        form = forms.BaseUserForm({'caption': 'bill-caption',
                                  'rationale': 'bill-rationale',
                                  'chronicle_on_accepted': 'chronicle-on-accepted',
                                  'duration': relations.BILL_DURATION.MONTH})

        self.assertFalse(form.is_valid())

    def test_duration__chronicle_on_ended(self):
        form = forms.BaseUserForm({'caption': 'bill-caption',
                                  'rationale': 'bill-rationale',
                                  'chronicle_on_accepted': 'chronicle-on-accepted',
                                  'chronicle_on_ended': 'chronicle-on-ended',
                                  'duration': relations.BILL_DURATION.MONTH})

        self.assertTrue(form.is_valid())


    def test_unlimited_duration__no_chronicle_on_ended(self):
        form = forms.BaseUserForm({'caption': 'bill-caption',
                                  'rationale': 'bill-rationale',
                                  'chronicle_on_accepted': 'chronicle-on-accepted',
                                  'duration': relations.BILL_DURATION.UNLIMITED})

        self.assertTrue(form.is_valid())

    def test_unlimited_duration__chronicle_on_ended(self):
        form = forms.BaseUserForm({'caption': 'bill-caption',
                                  'rationale': 'bill-rationale',
                                  'chronicle_on_accepted': 'chronicle-on-accepted',
                                  'chronicle_on_ended': 'chronicle-on-ended',
                                  'duration': relations.BILL_DURATION.UNLIMITED})

        self.assertFalse(form.is_valid())
