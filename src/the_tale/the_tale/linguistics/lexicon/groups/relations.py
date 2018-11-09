import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


class LEXICON_GROUP(rels_django.DjangoEnum):
    index_group = rels.Column()
    description = rels.Column(unique=False)
    variables = rels.Column(unique=False, no_index=True)

    records = (('ACTION_BATTLEPVE1X1', 0, 'Действие: сражение с монстром', 0,
                'Описание событий, происходящих при сражении с монстрами.',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.ACTOR: 'герой или монстр', V.ACTOR__WEAPON: 'оружие героя или монстра', V.DAMAGE: 'количество урона', V.EXPERIENCE: 'опыт', V.ARTIFACT: 'предмет', V.MOB: 'монстр', V.MOB__WEAPON: 'оружие монстра', V.COMPANION: 'спутник', V.COMPANION__WEAPON: 'оружие спутника', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_EQUIPPING', 1, 'Действие: экипировка', 10000,
                'Описание событий во время изменения экипировки героя.',
                {V.UNEQUIPPED: 'снимаемый артефакт', V.ITEM: 'артефакт', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.EQUIPPED: 'экипируемый артефакт', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_EVENT', 2, 'Небольшие события', 20000,
                'Описания небольших событий во время действий героя.',
                {V.PLACE: 'город', V.COINS: 'количество монет', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.EXPERIENCE: 'опыт', V.ARTIFACT: 'артефакт', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_IDLENESS', 3, 'Действие: бездействие героя', 30000,
                'Описание моментов, когда герой ничего не делает.',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_INPLACE', 4, 'Действие: посещение города', 40000,
                'Описание событий, происходящих при посещении героем города.',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.COINS: 'количество монет', V.ARTIFACT: 'предмет', V.SELL_PRICE: 'цена продажи', V.PERSON: 'житель', V.PLACE: 'город', V.EXPERIENCE: 'количество опыта', V.OLD_ARTIFACT: 'старый артефакт', V.COMPANION: 'спутник', V.COMPANION__WEAPON: 'оружие спутника', V.HEALTH: 'количество здоровья', V.ENERGY: 'энергия', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_MOVENEARPLACE', 5, 'Действие: путешествие в окрестностях города', 50000,
                'Описание действий, происходящих при путешествии героя в окрестностях города.',
                {V.PLACE: 'город', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_MOVETO', 6, 'Действие: путешествие между городами', 60000,
                'Описание событий при путешествии героя между городами (по дороге)',
                {V.DESTINATION: 'конечное место назначения', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.CURRENT_DESTINATION: 'текущее место назначения', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_QUEST', 7, 'Действие: выполнение задания', 70000,
                'Герой выполняет специфические для задания действия.',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_REGENERATE_ENERGY', 8, 'Действие: восстановление энергии', 80000,
                'Описание событий во время проведения героем религиозных обрядов.',
                {V.ENERGY: 'количество энергии', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_REST', 9, 'Действие: лечение', 90000,
                'Описание действий во время лечения героя.',
                {V.HEALTH: 'количество здоровья', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_RESURRECT', 10, 'Действие: воскрешение героя', 100000,
                'Описание событий при воскрешении героя',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_TRADING', 11, 'Действие: торговля', 110000,
                'Описание действий во время торговли',
                {V.COINS: 'количество монет', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.ARTIFACT: 'предмет', V.DATE: 'дата', V.TIME: 'время'}),

               ('ANGEL_ABILITY', 12, 'Способности: Хранитель', 120000,
                'Описание результата использование способностей игрока',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.DROPPED_ITEM: 'выкидываемый предмет', V.ENERGY: 'энергия', V.COINS: 'количество монет', V.EXPERIENCE: 'количество опыта', V.HEALTH: 'количество здоровья', V.MOB: 'монстр', V.MOB__WEAPON: 'оружие монстра', V.COMPANION: 'спутник', V.COMPANION__WEAPON: 'оружие спутника', V.DAMAGE: 'урон', V.DATE: 'дата', V.TIME: 'время'}),

               ('HERO_ABILITY', 14, 'Способности', 140000,
                'Описание применения способностей героем (или монстром)',
                {V.ATTACKER: 'атакующий', V.ATTACKER__WEAPON: 'оружие атакующего', V.HEALTH: 'количество вылеченного здоровья', V.DAMAGE: 'количество урона', V.ATTACKER_DAMAGE: 'количество урона по атакующему', V.ACTOR: 'герой или монстр', V.ACTOR__WEAPON: 'оружие героя или монстра', V.DEFENDER: 'защищающийся', V.DEFENDER__WEAPON: 'оружие защищающегося', V.COMPANION: 'спутник', V.COMPANION__WEAPON: 'оружие спутника', V.DATE: 'дата', V.TIME: 'время', V.ARTIFACT: 'артефакт'}),

               ('HERO_COMMON', 15, 'Общие сообщения, относящиеся к герою', 150000,
                'Сообщение, относящиеся к герою и не вошедшие в другие модули',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.LEVEL: 'уровень', V.ARTIFACT: 'артефакт', V.DATE: 'дата', V.TIME: 'время'}),

               ('META_ACTION_ARENA_PVP_1X1', 16, 'Действие: дуэль на арене', 160000,
                'Описание действий во время PvP дуэли на арене',
                {V.DUELIST_2: '2-ой участник дуэли', V.DUELIST_2__WEAPON: 'оружие 2 участника дуэли', V.DUELIST_1: '1-ый участник дуэли', V.DUELIST_1__WEAPON: 'оружие 1 участника дуэли', V.KILLER: 'победитель', V.KILLER__WEAPON: 'оружие победителя', V.ATTACKER: 'атакующий', V.ATTACKER__WEAPON: 'оружие атакующего', V.VICTIM: 'проигравший', V.VICTIM__WEAPON: 'оружие проигравшего', V.DATE: 'дата', V.TIME: 'время'}),

               ('PVP', 17, 'PvP: фразы', 170000,
                'Фразы, употребляющиеся при PvP.',
                {V.TEXT: 'любой текст', V.EFFECTIVENESS: 'изменение эффективности', V.DUELIST_2: '2-ой участник дуэли', V.DUELIST_2__WEAPON: 'оружие 2 участника дуэли', V.DUELIST_1: '1-ый участник дуэли', V.DUELIST_1__WEAPON: 'оружие 1 участника дуэли', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_CARAVAN', 18, 'Задание: провести караван', 180000,
                'Тексты, относящиеся к заданию.',
                {V.INITIATOR: 'житель, начинающий задание', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.ANTAGONIST_POSITION: 'место продажи награбленного', V.COINS: 'количество монет', V.ARTIFACT: 'артефакт', V.INITIATOR_POSITION: 'место начала задания', V.RECEIVER: 'житель, заканчивающий задание', V.RECEIVER_POSITION: 'место окончания задания', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_COLLECT_DEBT', 19, 'Задание: чужие обязательства', 190000,
                'Тексты, относящиеся к заданию.',
                {V.INITIATOR: 'житель, начинающий задание', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.COINS: 'количество монет', V.ARTIFACT: 'артефакт', V.INITIATOR_POSITION: 'место начала задания', V.RECEIVER: 'житель, заканчивающий задание', V.RECEIVER_POSITION: 'место окончания задания', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_DELIVERY', 20, 'Задание: доставить письмо', 200000,
                'Тексты, относящиеся к заданию',
                {V.INITIATOR: 'житель, начинающий задание', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.ANTAGONIST_POSITION: 'место скупки краденого', V.COINS: 'количество монет', V.ARTIFACT: 'артефакт', V.INITIATOR_POSITION: 'место начала задания', V.RECEIVER: 'житель, заканчивающий задание', V.RECEIVER_POSITION: 'место окончания задания', V.ANTAGONIST: 'житель, скупающий краденое', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_HELP', 21, 'Задание: помощь', 210000,
                'Тексты, относящиеся к заданию.',
                {V.INITIATOR: 'житель, начинающий задание', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.COINS: 'количество монет', V.ARTIFACT: 'артефакт', V.INITIATOR_POSITION: 'место начала задания', V.RECEIVER: 'житель, заканчивающий задание', V.RECEIVER_POSITION: 'место окончания задания', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_HELP_FRIEND', 22, 'Задание: помощь соратнику', 220000,
                'Тексты, относящиеся к заданию.',
                {V.RECEIVER_POSITION: 'место окончания задания', V.COINS: 'количество монет', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.ARTIFACT: 'артефакт', V.RECEIVER: 'житель, заканчивающий задание', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_HOMETOWN', 23, 'Задание: путешествие в родной город', 230000,
                'Тексты, относящиеся к заданию.',
                {V.RECEIVER_POSITION: 'место окончания задания', V.COINS: 'количество монет', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.INITIATOR_POSITION: 'место начала задания', V.ARTIFACT: 'артефакт', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_HUNT', 24, 'Задание: охота', 240000,
                'Тексты, относящиеся к заданию.',
                {V.RECEIVER_POSITION: 'место окончания задания', V.COINS: 'количество монет', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.ARTIFACT: 'артефакт', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_INTERFERE_ENEMY', 25, 'Задание: навредить противнику', 250000,
                'Тексты, относящиеся к заданию.',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.ANTAGONIST_POSITION: 'место деятельности противника', V.COINS: 'количество монет', V.ARTIFACT: 'артефакт', V.RECEIVER: 'противник', V.RECEIVER_POSITION: 'место жительства противника', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_PILGRIMAGE', 26, 'Задание: паломничество в святой город', 260000,
                'Тексты, относящиеся к заданию.',
                {V.RECEIVER_POSITION: 'место окончания задания', V.COINS: 'количество монет', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.INITIATOR_POSITION: 'место начала задания', V.ARTIFACT: 'артефакт', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_SEARCH_SMITH', 27, 'Задание: посещение кузнеца', 270000,
                'Тексты, относящиеся к заданию.',
                {V.UNEQUIPPED: 'снимаемый артефакт', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.COINS: 'цена работы кузнеца', V.ARTIFACT: 'артефакт', V.SELL_PRICE: 'цена продажи', V.RECEIVER: 'житель, заканчивающий задание', V.RECEIVER_POSITION: 'место окончания задания', V.DATE: 'дата', V.TIME: 'время'}),

               ('QUEST_SPYING', 28, 'Задание: шпионаж', 280000,
                'Тексты, относящиеся к заданию.',
                {V.INITIATOR: 'житель, начинающий задание', V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.COINS: 'количество монет', V.ARTIFACT: 'артефакт', V.INITIATOR_POSITION: 'место начала задания', V.RECEIVER: 'житель, заканчивающий задание', V.RECEIVER_POSITION: 'место окончания задания', V.DATE: 'дата', V.TIME: 'время'}),

               ('COMPANIONS', 29, 'Спутники', 290000,
                'Тексты, относящиеся к спутникам.',
                {V.COMPANION_OWNER: 'владелец спутника', V.COMPANION_OWNER__WEAPON: 'оружие владелеца спутника', V.COMPANION: 'спутник', V.COMPANION__WEAPON: 'оружие спутника', V.ATTACKER: 'атакущий спутника', V.ATTACKER__WEAPON: 'оружие того, кто атакует спутника', V.COINS: 'вырученные средства', V.EXPERIENCE: 'опыт', V.HEALTH: 'количество здоровья', V.MOB: 'монстр', V.MOB__WEAPON: 'оружие монстра', V.DESTINATION: 'место назначения', V.DAMAGE: 'урон', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_HEAL_COMPANION', 30, 'Действие: уход за спутником', 300000,
                'Герой ухаживает за спутником (обрабатывает раны, смазывает детальки, чистит карму, в зависимости от спутника).',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.COMPANION: 'спутник', V.COMPANION__WEAPON: 'оружие спутника', V.HEALTH: 'количество здоровья', V.DATE: 'дата', V.TIME: 'время'}),

               ('JOBS', 31, 'Занятия Мастеров', 310000,
                'Названия занятий и записи в дневник героев',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.PERSON: 'мастер', V.PLACE: 'город', V.COINS: 'монеты', V.ARTIFACT: 'артефакт', V.EXPERIENCE: 'опыт', V.ENERGY: 'энергия', V.DATE: 'дата', V.TIME: 'время'}),

               ('ACTION_FIRST_STEPS', 32, 'Действие: первые шаги героя', 320000,
                '''
<p>Герой только что завершил инициацию и осознаёт свою новую роль в мире.</p>

<p>Во фразах этой группы рекомендуется активно использовать ограничения переменной героя по свойствам, задаваемым игроком во время его создания.</p>''',
                {V.HERO: 'герой', V.HERO__WEAPON: 'оружие героя', V.PLACE: 'город', V.DATE: 'дата', V.TIME: 'время'}),

               ('HERO_HISTORY', 33, 'Предыстория героя', 330000,
                '''
<p>Фразы описания предыстории героя (до первой смерти включительно).</p>

<p>Предыстория героя строится из трёх частей: детсво (происхождение), юношество (становление), смерть (финал).</p>

<p>Во фразах истории для переменной героя допустимо использовать только следующие ограничения:</p>

<ul>
  <li>пол;</li>
  <li>раса;</li>
  <li>честь: только порочный или порядочный;</li>
  <li>миролюбие: только задира или добрхот;</li>
  <li>архетип;</li>
  <li>воспитание;</li>
  <li>способ первой смерти;</li>
  <li>возраст первой смерти.</li>
</ul>

<p>Для истории всегда выбирается фраза, которая по б<b>о</b>льшему количеству ограничений соответствует параметрам героя.</p>

<p>Для одного типа фраз истории нельзя создать два шаблона с одинаковыми ограничениями.</p>

               ''',
                {V.HERO: 'герой'}),

               )
