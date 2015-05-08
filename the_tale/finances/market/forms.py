# coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields

from the_tale.finances.market import conf


class PriceForm(forms.Form):

    price = fields.IntegerField(label=u'Цена')


    def clean_price(self):
        price = self.cleaned_data['price']

        if price < conf.settings.MINIMUM_PRICE:
            raise ValidationError(u'Цена должна быть не меньше %(min_price)s печенек' % {'min_price': conf.settings.MINIMUM_PRICE})

        return price
