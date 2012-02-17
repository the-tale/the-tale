# coding: utf-8

import random


class Generator(object):

    def __init__(self):
        pass

    def msg_action_idleness_waiting(self, hero):
        return random.choice([u'А не поплевать ли мне в потолок...',
                              u'Раз дощечка, два дощечка - какой же длинный забор',
                              u'"Чего смотришь? У меня перекур"'])

    def msg_action_idleness_start_quest(self, hero):
        return random.choice([u'Ну всё, хвати баклуши бить, пора на подвиги',
                              u'Эх, ща покажу силушку богатырскую',
                              u'Пока в путь, пока совесть не загрызла'])

    def msg_action_moveto_start(self, hero, destination):
        return random.choice([u'Где тут ближайшая дорога в %(destination)s',
                              u'Вперёд! На встречу подвигам! А подвиги, по слухам, лучше всего совершать в %(destination)s',
                              u'Пора выходить - дорога в %(destination)s не близкая']) % {'destination': destination.name}

    def msg_action_moveto_move(self, hero, destination, current_destination):
        return random.choice([u'Ну и грязища, а по этой дороге ещё и караваны водят...',
                              u'Поля, луга, перелески, скелет в овражке - до чего красива родная природа',
                              u'И в мороз и в жару герой должен двигать ногами']) % {'destination': destination.name}

    def msg_action_battlepve1x1_start(self, hero, mob):
        return random.choice([u'Ужасный %(mob)s выскочил из кустов',
                              u'Как %(hero)s ни пытался притвориться мёртвым, %(mob)s всё равно пошёл в наступление',
                              u'%(mob)s на горизонте, в бой!']) % {'hero': hero.name,
                                                                   'mob': mob.name}

    def msg_action_battlepve1x1_battle_stun(self, actor):
        return random.choice([u'%(actor)s дезариентирован и не может атаковать',
                              u'%(actor)s с увлеченеим ловит летающие вокруг голову звёздочки',
                              u'%(actor)s было подумал ударить, но оказался не в состоянии додумать мысль']) % {'actor': actor.name}

    def msg_action_battlepve1x1_battle_miss(self, actor, ability, enemy):
        subsitutions = {'actor': actor.name,
                        'ability': ability.name,
                        'enemy': enemy.name}
        return random.choice([u'%(actor)s попытался использовать способность %(ability)s, но противник ловко увернулся',
                              u'у %(actor)s почти получилось использовать %(ability)s, но %(enemy)s вовремя отскочил в сторону',
                              u'%(enemy)s пустил в глаза противника солнечный зайчик, из-за чего тот не смог использовать %(ability)s',
                              u'Солнце ослепило %(actor)s и тот промахнулся по %(enemy)s']) % subsitutions

    #######################################
    # hero abilities
    #######################################

    def msg_hability_hit(self, attacker, defender, damage):
        return random.choice([u'%(attacker)s поднатужился и нанёс %(damage)s урона',
                              u'Умелая подсечка и придорожный камень нанёс голове %(defender)s %(damage)s урона',
                              u'Аперкот и вокруг %(defender)s летает %(damage)s звёздочек',
                              u'%(attacker)s поцарапал %(defender)s на %(damage)s HP',
                              u'%(attacker)s отошёл в сторону и %(defender)s с разбега врезался в стену, потеряв %(damage)s HP',
                              u'%(defender)s пропустил удар в живот и теперь страдает отсутствием %(damage)s HP']) % {'attacker': attacker.name,
                                                                                                                      'defender': defender.name,
                                                                                                                      'damage': damage}

    def msg_hability_magicmushroom(self, actor):
        return random.choice([u'"Волшебный гриб!" - воскликнул %(actor)s, запихивая в рот миловидный гриб с красной в белую крапинку шапочкой']) % {'actor': actor.name}
        

    def msg_hability_sidestep(self, actor):
        return random.choice([u'%(actor)s ловко ушёл в сторону от противника']) % {'actor': actor.name}

    def msg_hability_runuppush(self, attacker, defender, damage):
        return random.choice([u'%(attacker)s разбежался и впечатал %(defender)s в дерево,  нанеся%(damage)s урона']) % {'attacker': attacker.name,
                                                                                                                        'defender': defender.name,
                                                                                                                        'damage': damage}
    def msg_hability_regeneration(self, actor, health):
        return random.choice([u'%(actor)s восстановил %(health)d HP']) % {'actor': actor.name,
                                                                          'health': health}

    ########################################
    
    def msg_action_battlepve1x1_hero_killed(self, hero, mob):
        return random.choice([u'%(mob)s провёл завершающий удар и тело героя упало в авраг',
                              u'"Вот она! Справделивость!" - закричал %(mob)s пиная безжизненное тело своего противника',
                              u'%(hero)s пошатнулся и рухнул в ноги %(mob)s']) % {'hero': hero.name,
                                                                                  'mob': mob.name}

    def msg_action_battlepve1x1_mob_killed(self, hero, mob):
        return random.choice([u'"Фаталити!" - закричал герой, нанося завершающий удар',
                              u'Герой вытер оружие и принялся деловито обыскивать поверженого %(mob)s',
                              u'%(mob)s не выдержал геройского напора и покончил жизнь самоубийством']) % {'hero': hero.name,
                                                                                                           'mob': mob.name}

    def msg_action_restinsettlement_start(self, hero):
        return random.choice([u'%(hero)s решил отдухонуть и залечить раны',
                              u'Отправился искать подорожник',
                              u'Йод, касторка, спирт, теперь надо всё это смешать и выпить, глядишь - поможет']) % {'hero': hero.name}

    def msg_action_restinsettlement_resring(self, hero, heal_amount):
        return random.choice([u'Ух ты, а подорожник помогает, вылечил %(heal_amount)s HP',
                              u'Применил магию вуду и исцелился на %(heal_amount)s HP',
                              u'Проходящий мимо шаман кастанул чайник и исцелил на %(heal_amount)s HP']) % {'hero': hero.name,
                                                                                                            'heal_amount': heal_amount}

    def msg_action_equipinsettlement_start(self, hero):
        return random.choice([u'Герой решил просмотреть своё барахло, может что сгодится',
                              u'Столько добычи, неужели среди этого мусора не найдётся чего-нибудь полезного',
                              u'Добыча счёт любит, надо бы её посчитать']) % {'hero': hero.name}

    def msg_action_equipinsettlement_change_item(self, hero, unequipped, equipped):
        return random.choice([u'Что-то %(unequipped)s поизносился, надо заменить его на %(equipped)s',
                              u'%(equipped)s - хорошая замена для %(unequipped)s',
                              u'%(unequipped)s уже никуда не годится, а вот %(equipped)s - другое дело']) % {'hero': hero.name,
                                                                                                             'unequipped': unequipped.name,
                                                                                                             'equipped': equipped.name}

    def msg_action_equipinsettlement_equip_item(self, hero, equipped):
        return random.choice([u'%(equipped)s здорово мне подойдёт',
                              u'%(hero)s с удовольствием примерил %(equipped)s',
                              u'%(hero)s решил, что %(equipped)s как нельзя лучше подойдёт его образу']) % {'hero': hero.name,
                                                                                                            'equipped': equipped.name}

    def msg_action_tradeinsettlement_start(self, hero):
        return random.choice([u'Люд говорит, что сегодня ярмарка, надо бы её навестить',
                              u'Пора заняться комерцией',
                              u'Ой, мне кажется этот торговец смотрит на меня, надо бежать']) % {'hero': hero.name}


    def msg_action_tradeinsettlement_sell_item(self, hero, artifact, sell_price):
        return random.choice([u'Всего %(sell_price)s монет за %(artifact)s?! Да они издеваются!',
                              u'Отличная цена за %(artifact)s. Положил %(sell_price)s монет в кошелёк.',
                              u'Глупый торговец, отдал %(sell_price)s монет за какой-то %(artifact)s']) % {'hero': hero.name,
                                                                                                           'artifact': artifact.name,
                                                                                                           'sell_price': sell_price}

    def msg_action_movenearplace_walk(self, hero, place):
        return random.choice([u'Оказывается, окрестности %(place)s очень живописны',
                              u'Век живи - век учить, оказывется рядом с %(place)s водятся гигантские многоножки',
                              u'Ну и грязища, второй раз за день вступил в лужу']) % {'hero': hero.name,
                                                                                      'place': place.name}

    def msg_ability_shortteleport_activate(self, hero):
        return random.choice([u'Порыв ветра поднял %(hero)s в воздух и пронёс до ближайшего дерева',
                              u'"Дырка в пространстве - единственный достойный героя способ передвижения"',
                              u'"Хранитель, зачем так пинаться-то?"']) % {'hero': hero.name}

    
    def msg_ability_lightning_activate(self, hero, mob):
        return random.choice([u'Молния существенно поджарила %(mob)s',
                              u'Вот значит как работают вакуумные бомбы',
                              u'Бабочка неудачно приземлилась на противника, выведя того из равновесия, результат - серьёзная шика у %(mob)s']) % {'hero': hero.name,
                                                                                                                                                   'mob': mob.name}

    
    def msg_ability_healhero_activate(self, hero, heal_amount):
        return random.choice([u'Герой исцелён на %(heal_amount)s HP',
                              u'Банка с йодом? Что мне с ней сделать, выпить?',
                              u'Ха-ха, божественная регенерация!']) % {'hero': hero.name,
                                                                       'heal_amount': heal_amount}

    
    def msg_ability_getquest_activate(self, hero):
        return random.choice([u'Что-то совестно мне стало без дела сидеть',
                              u'Опять шило в заднице колоть начало',
                              u'Попытался поспать, но упал с кровати, придётся идти на подвиги ']) % {'hero': hero.name}


    def msg_quests_get_reward(self, hero):
        return random.choice([u'О Боги! Когда же я наконец получу хоть что-нибудь в награду за труды?']) % {'hero': hero.name}


    def msg_heroes_put_loot(self, hero, artifact):
        return random.choice([u'%(artifact)s самое место у меня в рюкзаке',
                              u'%(hero)s воровато озираясь прикарманил %(artifact)s',
                              u'Неплохая вещица, этот %(artifact)s, надо оставить себе']) % {'hero': hero.name,
                                                                                             'artifact': artifact.name}

    def msg_heroes_put_loot_no_space(self, hero, artifact):
        return random.choice([u'%(artifact)s никак не влазит в рюкзак, придётся его выкинуть',
                              u'%(artifact)s остался валяться на обочине дороги',
                              u'оставлю я %(artifact)s сдесь, может кому сгодится']) % {'hero': hero.name,
                                                                                        'artifact': artifact.name}
