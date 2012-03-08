# coding: utf-8

from .models import Word, WORD_TYPE
from .exceptions import TextgenException
from .logic import efication, get_gram_info

WORD_CONSTRUCTORS = {}

class PROPERTIES(object):
    CASES = (u'им', u'рд', u'дт', u'вн', u'тв', u'пр')
    ANIMACYTIES = (u'од', u'но')
    NUMBERS = (u'ед', u'мн')
    GENDERS = (u'мр', u'жр', u'ср')
    TIMES = (u'нст', u'прш', u'буд')
    PERSONS = (u'1л', u'2л', u'3л')

    @classmethod
    def is_argument_available(cls, arg):
        return (arg in cls.CASES or
                arg in cls.ANIMACYTIES or
                arg in cls.NUMBERS or
                arg in cls.GENDERS or
                arg in cls.TIMES or
                arg in cls.PERSONS)


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

    @classmethod
    def pluralize_args(cls, number, args):
        raise NotImplementedError

    def pluralize(self, number, args):
        return self.get_form(self.pluralize_args(number, args.get_copy()))

    def update_args(self, arguments, dependence_class, dependence_args):
        raise NotImplementedError

    @classmethod
    def create_from_baseword(cls, src, tech_vocabulary={}):
        raise NotImplementedError
    
    @staticmethod
    def create_from_model(model):
        properties = model.properties.split(u'|')
        if properties == [u'']:
            properties = ()
        return WORD_CONSTRUCTORS[model.type](normalized=model.normalized,
                                             forms=model.forms.split(u'|'),
                                             properties=properties)

    @staticmethod
    def create_from_string(morph, string, tech_vocabulary={}):
        normalized = efication(string.upper())

        if ' ' in string:
            return WORD_CONSTRUCTORS[WORD_TYPE.NOUN_GROUP].create_from_baseword(morph, string, tech_vocabulary)

        class_, normalized, properties = get_gram_info(morph, normalized, tech_vocabulary)

        if class_ == u'С':
            return WORD_CONSTRUCTORS[WORD_TYPE.NOUN].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'П':
            return WORD_CONSTRUCTORS[WORD_TYPE.ADJECTIVE].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'Г':
            return WORD_CONSTRUCTORS[WORD_TYPE.VERB].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'МС':
            return WORD_CONSTRUCTORS[WORD_TYPE.NOUN].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'МС-П':
            return WORD_CONSTRUCTORS[WORD_TYPE.ADJECTIVE].create_from_baseword(morph, string, tech_vocabulary)
        else:
            raise TextgenException(u'unknown word type: %s' % (string, ) )
        

    def save_to_model(self):
        return Word.objects.create(normalized=self.normalized,
                                   type=self.TYPE,
                                   forms=u'|'.join(self.forms),
                                   properties=u'|'.join(self.properties))

class Fake(WordBase):

    TYPE = WORD_TYPE.FAKE

    def __init__(self, word):
        super(Fake, self).__init__(normalized=word.lower(), forms=[word], properties=())

    def get_form(self, args):
        return self.forms[0]

    @classmethod
    def pluralize_args(cls, number, args):
        return args

    def update_args(self, arguments, dependence, dependence_args):
        pass


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

    def update_args(self, arguments, dependence, dependence_args):
        if isinstance(dependence, Noun):
            arguments.number = dependence_args.number

        elif isinstance(dependence, Numeral):
            self.pluralize_args(dependence.normalized, arguments)

    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        class_, normalized, properties = get_gram_info(morph, efication(src.upper()), tech_vocabulary)

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
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        class_, normalized, properties = get_gram_info(morph, efication(src.upper()), tech_vocabulary)

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
                return self.forms[3]
            else:
                return self.forms[PROPERTIES.GENDERS.index(args.gender)]
        elif args.time == u'нст':
            delta = len(PROPERTIES.GENDERS) + 1
            return self.forms[delta + len(PROPERTIES.NUMBERS) * PROPERTIES.PERSONS.index(args.person) + PROPERTIES.NUMBERS.index(args.number)]
        elif args.time == u'буд':
            delta = len(PROPERTIES.GENDERS) + 1 + len(PROPERTIES.NUMBERS) * len(PROPERTIES.PERSONS)
            return self.forms[delta + len(PROPERTIES.NUMBERS) * PROPERTIES.PERSONS.index(args.person) + PROPERTIES.NUMBERS.index(args.number)]

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

    def update_args(self, arguments, dependence, dependence_args):
        if isinstance(dependence, Noun):
            arguments.number = dependence_args.number
            arguments.gender = dependence_args.gender

        elif isinstance(dependence, Numeral):
            self.pluralize_args(dependence.normalized, arguments)


    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        class_, normalized, properties = get_gram_info(morph, efication(src.upper()), tech_vocabulary)

        base = morph.inflect_ru(efication(src.upper()), u'ед,мр', u'Г')

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


class NounGroup(Noun):

    TYPE = WORD_TYPE.NOUN_GROUP

    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        '''
        one noun MUST be in им
        there are problems with nouns in multiple number: рога
        '''
        main_noun = None

        phrase = []
        for word in src.split(' '):
            if word:
                class_, norm, properties = get_gram_info(morph, efication(word.upper()), tech_vocabulary)
                if class_ == u'С':
                    if u'им' in properties:
                        main_noun = norm                 
                        phrase.append((class_, norm, False))
                    else:
                        phrase.append((class_, word, True))
                else:
                    phrase.append((class_, norm, False))

        gram_info = morph.get_graminfo(main_noun.upper())[0]

        info = gram_info['info']

        if u'мр' in info:
            properties = [u'мр']
        elif u'ср' in info:
            properties = [u'ср']
        else:
            properties = [u'жр']

        forms = []

        for number in PROPERTIES.NUMBERS:

            additional_properties = []
            if number == u'ед':
                additional_properties = properties

            for case in PROPERTIES.CASES:
                phrase_form = []
                
                for class_, word, constant in phrase:
                    if constant:
                        phrase_form.append(word)
                    else:
                        phrase_form.append(morph.inflect_ru(word, u','.join([case, number]+additional_properties), class_ ).lower())
                forms.append( ' '.join(phrase_form))

        normalized = ' '.join([word for class_, word, constant in phrase])

        return cls(normalized=normalized.lower(), forms=forms, properties=properties)



WORD_CONSTRUCTORS = dict([(class_.TYPE, class_) 
                          for class_name, class_ in globals().items()
                          if isinstance(class_, type) and issubclass(class_, WordBase) and class_ != WordBase])



