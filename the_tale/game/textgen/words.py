# coding: utf-8

from .models import Word, WORD_TYPE, PROPERTIES
from .exceptions import TextgenException

WORD_CONSTRUCTORS = {}

class Args(object):

    __slots__ = ('case', 'number', 'gender', 'time', 'person')

    def __init__(self, *args):
        self.case = u'им'
        self.number = u'ед'
        self.gender = u'мр'
        self.time = u'нст'
        self.person = u'1л'
        self.update(*args)

    def get_copy(self):
        return self.__class__(self.case, self.number, self.gender, self.time, self.person)

    def update(self, *args):
        for arg in args:
            if arg in PROPERTIES.CASES:
                self.case = arg
            elif arg in PROPERTIES.NUMBERS:
                self.number = arg
            elif arg in PROPERTIES.GENDERS:
                self.gender = arg
            elif arg in PROPERTIES.TIMES:
                self.time = arg
            elif arg in PROPERTIES.PERSONS:
                self.person = arg

    def __unicode__(self):
        return u'<%s, %s, %s, %s>' % (self.case, self.number, self.gender, self.time)

    def __str__(self): return self.__unicode__()


class WordBase(object):

    TYPE = None
    
    def __init__(self, normalized, forms, properties):
        self.normalized = normalized
        self.forms = tuple(forms)
        self.properties = tuple(properties)

    def get_form(self, args):
        raise NotImplementedError


    def pluralize(self, number, args):
        raise NotImplementedError

    def update_args(self, arguments, dependence_class, dependence_args):
        raise NotImplementedError

    @classmethod
    def create_from_baseword(cls, src):
        raise NotImplementedError
    
    @staticmethod
    def create_from_model(model):
        properties = model.properties.split(u'|')
        if properties == [u'']:
            properties = ()
        return WORD_CONSTRUCTORS[model.type](normalized=model.normalized,
                                             forms=model.forms.split(u'|'),
                                             properties=properties)

    def save_to_model(self):
        # Word.objects.filter(normalized=self.normalized).delete()
        return Word.objects.create(normalized=self.normalized,
                                   type=self.TYPE,
                                   forms=u'|'.join(self.forms),
                                   properties=u'|'.join(self.properties))


class Noun(WordBase):

    TYPE = WORD_TYPE.NOUN

    @property
    def gender(self): return self.properties[0]

    def get_form(self, args):
        return self.forms[PROPERTIES.NUMBERS.index(args.number) * len(PROPERTIES.CASES) + PROPERTIES.CASES.index(args.case)]

    @classmethod
    def pluralize_args(cls, number, args):
        if number % 10 == 1 and number != 11:
            args.update(u'ед')
        elif 2 <= number % 10 <= 4 and not (12 <= number <= 14):
            args.update(u'мн')
        else:
            args.update(u'мн')
            if args.case == u'им':
                args.update(u'рд')

        return args


    def pluralize(self, number, args):
        return self.get_form(self.pluralize_args(number, args.get_copy()))

    def update_args(self, arguments, dependence, dependence_args):
        if isinstance(dependence, Noun):
            arguments.number = dependence_args.number

        elif isinstance(dependence, Numeral):
            self.pluralize_args(dependence.normalized, arguments)

    @classmethod
    def create_from_baseword(cls, morph, src):
        normalized = morph.normalize(src.upper())

        if len(normalized) != 1:
            raise TextgenException(u'can not determine type of word: %s' % src)

        normalized = list(normalized)[0]

        forms = []

        for number in PROPERTIES.NUMBERS:
            for case in PROPERTIES.CASES:
                forms.append(morph.inflect_ru(normalized, u'%s,%s' % (case, number) ).lower() )

        gram_info = morph.get_graminfo(normalized)[0]

        info = gram_info['info']

        if u'мр' in info:
            properties = [u'мр']
        elif u'ср' in info:
            properties = [u'ср']
        else:
            properties = [u'жр']

        return cls(normalized=normalized.lower(), forms=forms, properties=properties)


class Numeral(WordBase):

    TYPE = WORD_TYPE.NUMERAL

    def __init__(self, number):
        super(Numeral, self).__init__(normalized=number, forms=[number], properties=[])

    def get_form(self, args):
        return self.forms[0]

    def update_args(self, arguments, dependence, dependence_args):
        pass


class Adjective(WordBase):

    TYPE = WORD_TYPE.ADJECTIVE

    def get_form(self, args):
        if args.number == u'ед':
            return self.forms[PROPERTIES.GENDERS.index(args.gender) * len(PROPERTIES.CASES) + PROPERTIES.CASES.index(args.case)]
        else:
            delta = len(PROPERTIES.CASES) * len(PROPERTIES.GENDERS)
            return self.forms[delta + PROPERTIES.CASES.index(args.case)]

    def update_args(self, arguments, dependence_class, dependence_args):
        if isinstance(dependence_class, Noun):
            arguments.number = dependence_args.number
            arguments.gender = dependence_args.gender
            arguments.case = dependence_args.case

    @classmethod
    def create_from_baseword(cls, morph, src):
        normalized = morph.normalize(src.upper())

        if len(normalized) != 1:
            raise TextgenException(u'can not determine type of word: %s' % src)

        normalized = list(normalized)[0]

        forms = []

        # single
        for gender in PROPERTIES.GENDERS:
            for case in PROPERTIES.CASES:
                forms.append(morph.inflect_ru(normalized, u'%s,%s,ед' % (case, gender) ).lower() )

        #multiple
        for case in PROPERTIES.CASES:
            forms.append(morph.inflect_ru(normalized, u'%s,%s' % (case, u'мн') ).lower() )
        
        return cls(normalized=normalized.lower(), forms=forms, properties=[])


class Verb(WordBase):

    TYPE = WORD_TYPE.VERB

    def get_form(self, args):

        if args.time == u'прш':
            if args.number == u'мн':
                return self.forms[4]
            else:
                return self.forms[PROPERTIES.GENDERS.index(args.gender)]
        elif args.time == u'нст':
            delta = len(PROPERTIES.GENDERS) + 1
            return self.forms[delta + len(PROPERTIES.NUMBERS) * PROPERTIES.PERSONS.index(args.person) + PROPERTIES.NUMBERS.index(args.number)]
        elif args.time == u'буд':
            delta = len(PROPERTIES.GENDERS) + 1 + len(PROPERTIES.NUMBERS) * len(PROPERTIES.PERSONS)
            return self.forms[delta + len(PROPERTIES.NUMBERS) * PROPERTIES.PERSONS.index(args.person) + PROPERTIES.NUMBERS.index(args.number)]

    def pluralize(self, number, case):
        raise NotImplementedError

    def update_args(self, arguments, dependence_class, dependence_args):
        if isinstance(dependence_class, Noun):
            arguments.number = dependence_args.number
            arguments.gender = dependence_args.gender


    @classmethod
    def create_from_baseword(cls, morph, src):
        normalized = morph.normalize(src.upper())

        base = morph.inflect_ru(src.upper(), u'ед,мр', u'Г')

        if len(normalized) != 1:
            raise TextgenException(u'can not determine type of word: %s' % src)
        normalized = list(normalized)[0]

        forms = [morph.inflect_ru(base, u'прш,мр,ед').lower(),
                 morph.inflect_ru(base, u'прш,жр,ед').lower(),
                 morph.inflect_ru(base, u'прш,ср,ед').lower(),
                 morph.inflect_ru(base, u'прш,мн').lower(),
                 morph.inflect_ru(base, u'нст,1л,ед').lower(),
                 morph.inflect_ru(base, u'нст,1л,мн').lower(),
                 morph.inflect_ru(base, u'нст,2л,ед').lower(),
                 morph.inflect_ru(base, u'нст,2л,мн').lower(),
                 morph.inflect_ru(base, u'нст,3л,ед').lower(),
                 morph.inflect_ru(base, u'нст,3л,мн').lower(),
                 morph.inflect_ru(base, u'буд,1л,ед').lower(),
                 morph.inflect_ru(base, u'буд,1л,мн').lower(),
                 morph.inflect_ru(base, u'буд,2л,ед').lower(),
                 morph.inflect_ru(base, u'буд,2л,мн').lower(),
                 morph.inflect_ru(base, u'буд,3л,ед').lower(),
                 morph.inflect_ru(base, u'буд,3л,мн').lower()]

        return cls(normalized=normalized.lower(), forms=forms, properties=[])


WORD_CONSTRUCTORS = dict([(class_.TYPE, class_) 
                          for class_name, class_ in globals().items()
                          if isinstance(class_, type) and issubclass(class_, WordBase) and class_ != WordBase])

