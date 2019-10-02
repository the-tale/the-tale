

import unittest

from .. import constants as c


class ConstantsTest(unittest.TestCase):

    def test_constants_values(self):

        self.assertEqual(c.EXPECTED_EVENT_LENGTH, 7)

        self.assertEqual(c.EMISSARY_RECEIVE_PERIOD_FOR_NEW_CLAN, 21)
        self.assertEqual(c.EXPECTED_EMISSARY_RECEIVE_PERIOD_FOR_TOP_CLAN, 7)

        self.assertEqual(c.SIMULTANEOUS_EMISSARY_EVENTS, 2)

        self.assertEqual(c.INITIAL_POINTS_IN_DAY, 1000)

        self.assertEqual(c.PRICE_START_EVENT, 1000)
        self.assertEqual(c.PRICE_CREATE_EMISSARY, 18000)
        self.assertEqual(c.PRICE_MOVE_EMISSARY, 1000)
        self.assertEqual(c.PRICE_DISMISS_EMISSARY, 1000)

        self.assertEqual(c.TOP_CARD_POINTS_BONUS, 100)

        self.assertEqual(c.INITIAL_MEMBERS_MAXIMUM, 5)
        self.assertEqual(c.INITIAL_EMISSARY_MAXIMUM, 2)
        self.assertEqual(c.INITIAL_FREE_QUESTS_MAXIMUM, 2)
        self.assertEqual(c.INITIAL_POINTS_GAIN, 857)
        self.assertEqual(c.INITIAL_POINTS, 19000)
        self.assertEqual(c.INITIAL_FREE_QUESTS, 2)
        self.assertEqual(c.INITIAL_EMISSARY_POWER, 1000)

        self.assertEqual(c.MAXIMUM_POINTS_GAIN, 2571)
        self.assertEqual(c.MAXIMUM_EMISSARIES, 10)

        self.assertEqual(c.MAXIMUM_MEMBERS, 100)

        self.assertEqual(c.MAXIMUM_FREE_QUESTS, 10)

        self.assertEqual(c.MAXIMUM_POINTS, 36000)

        self.assertEqual(c.EMISSARY_MAXIMUM_LEVEL_STEPS, 8)
        self.assertEqual(c.POINTS_GAIN_LEVEL_STEPS, 20)
        self.assertEqual(c.MEMBERS_MAXIMUM_LEVEL_STEPS, 95)

        self.assertEqual(c.EXPECTED_LEVELING_TIME, 5 * 365)

        self.assertEqual(c.POINTS_GAIN_INCREMENT_ON_LEVEL_UP, 85)

        self.assertEqual(c.EXPERIENCE_IN_DAY_ON_START, 400)
        self.assertEqual(c.EXPERIENCE_IN_DAY_ON_END, 2000)

        self.assertEqual(c.MINIMUM_TIME_TO_EMISSARY_LEVEL, 7)
        self.assertEqual(c.MINIMUM_TIME_TO_MEMBERS_LEVEL, 3)

        self.assertEqual(c.EMISSARY_MAXIMUM_LEVELS_TIME,
                        [7.0,
                         11.64532009960385,
                         19.37335431746249,
                         32.22984463284185,
                         53.61812250142036,
                         89.200028524116,
                         148.39469786530356,
                         246.87196538935143])
        self.assertEqual(c.POINTS_GAIN_LEVELS_TIME,
                         [7.0,
                          7.952430422184989,
                          9.034449945670474,
                          10.263690656522485,
                          11.66018368868932,
                          13.246685642028304,
                          15.04904941325528,
                          17.09664548270521,
                          19.422840521996637,
                          22.065541121767634,
                          25.067811499816976,
                          28.478575255534746,
                          32.3534126060856,
                          36.75546609573406,
                          41.7564695373292,
                          47.437916953099645,
                          53.892390563273516,
                          61.22506946280736,
                          69.55544357091692,
                          79.01926078313299])

        self.assertEqual(c.FREE_QUESTS_MAXIMUM_LEVELS_TIME,
                         [7.0,
                          11.64532009960385,
                          19.37335431746249,
                          32.22984463284185,
                          53.61812250142036,
                          89.200028524116,
                          148.39469786530356,
                          246.87196538935143])

        self.assertEqual(c.MEMBERS_MAXIMUM_LEVELS_TIME,
                         [3.0,
                          3.097268411074765,
                          3.1976905367472,
                          3.301368629286604,
                          3.408408256267532,
                          3.5189184080612828,
                          3.63301160881257,
                          3.750804031014362,
                          3.8724156137975587,
                          3.9979701850559586,
                          4.127595587530851,
                          4.26142380898363,
                          4.399591116588967,
                          4.542238195685387,
                          4.6895102930245285,
                          4.841557364664946,
                          4.9985342286610415,
                          5.160600722702603,
                          5.327921866865458,
                          5.500668031638958,
                          5.679015111401384,
                          5.8631447035199145,
                          6.053244293257517,
                          6.249507444675032,
                          6.452133997722852,
                          6.661330271722843,
                          6.877309275447747,
                          7.100290924011929,
                          7.330502262794334,
                          7.568177698621659,
                          7.813559238447126,
                          8.066896735767894,
                          8.328448145032011,
                          8.598479784293957,
                          8.877266606386211,
                          9.165092478882963,
                          9.462250473141038,
                          9.769043162712329,
                          10.085782931431604,
                          10.412792291493384,
                          10.750404211841758,
                          11.098962457207527,
                          11.458821938137877,
                          11.830349072374986,
                          12.213922157951565,
                          12.60993175838317,
                          13.018781100349553,
                          13.440886484269946,
                          13.876677708190353,
                          14.326598505414449,
                          14.791106996323705,
                          15.270676154846786,
                          15.765794290053204,
                          16.276965543361563,
                          16.804710401868725,
                          17.349566228322505,
                          17.912087808277615,
                          18.492847914991895,
                          19.092437892638074,
                          19.711468258424922,
                          20.35056932424081,
                          21.01039183845273,
                          21.691607648514232,
                          22.394910385056964,
                          23.121016168162377,
                          23.870664336532748,
                          24.64461820030395,
                          25.443665818266545,
                          26.26862080028658,
                          27.120323135743046,
                          27.999640048825682,
                          28.9074668815639,
                          29.844728005485933,
                          30.81237776283665,
                          31.811401438312167,
                          32.84281626230087,
                          33.90767244665236,
                          35.00705425402885,
                          36.14208110192801,
                          37.31390870250128,
                          38.52373023932833,
                          39.77277758234578,
                          41.06232254216739,
                          42.39367816507276,
                          43.768200069983294,
                          45.18728782878652,
                          46.652386391414566,
                          48.16498755712753,
                          49.72663149350007,
                          51.33890830465778,
                          53.00345965036015,
                          54.7219804175788,
                          56.4962204462729,
                          58.327986311119105,
                          60.21914316101017])

        self.assertEqual(c.EXPERIENCE_PER_EVENT, 100)

        self.assertEqual(c.EMISSARY_MEXIMUM_LEVELS_EXPERIENCE,
                         [2900,
                          5100,
                          9200,
                          17500,
                          35100,
                          75200,
                          171500,
                          413600])

        self.assertEqual(c.POINTS_GAIN_LEVELS_EXPERIENCE,
                         [2900,
                          3400,
                          4100,
                          4900,
                          5900,
                          7100,
                          8700,
                          10600,
                          12900,
                          15900,
                          19600,
                          24300,
                          30200,
                          37600,
                          47100,
                          59000,
                          74200,
                          93600,
                          118300,
                          149800])

        self.assertEqual(c.FREE_QUESTS_MAXIMUM_LEVELS_EXPERIENCE,
                         [2900,
                          5100,
                          9200,
                          17500,
                          35100,
                          75200,
                          171500,
                          413600])

        self.assertEqual(c.MEMBERS_MAXIMUM_LEVELS_EXPERIENCE,
                         [1200,
                          1300,
                          1300,
                          1400,
                          1400,
                          1500,
                          1500,
                          1600,
                          1600,
                          1700,
                          1800,
                          1900,
                          1900,
                          2000,
                          2100,
                          2200,
                          2300,
                          2400,
                          2500,
                          2600,
                          2700,
                          2800,
                          2900,
                          3100,
                          3200,
                          3300,
                          3500,
                          3600,
                          3800,
                          4000,
                          4200,
                          4400,
                          4600,
                          4800,
                          5000,
                          5200,
                          5500,
                          5700,
                          6000,
                          6300,
                          6600,
                          6900,
                          7300,
                          7600,
                          8000,
                          8400,
                          8800,
                          9300,
                          9700,
                          10200,
                          10700,
                          11300,
                          11900,
                          12500,
                          13100,
                          13800,
                          14500,
                          15300,
                          16100,
                          17000,
                          17900,
                          18800,
                          19800,
                          20900,
                          22100,
                          23300,
                          24500,
                          25900,
                          27300,
                          28900,
                          30500,
                          32200,
                          34000,
                          35900,
                          38000,
                          40100,
                          42400,
                          44800,
                          47400,
                          50200,
                          53100,
                          56200,
                          59400,
                          62900,
                          66600,
                          70500,
                          74700,
                          79100,
                          83800,
                          88800,
                          94100,
                          99700,
                          105700,
                          112100,
                          118800])

        self.assertEqual(c.EMISSARY_POWER_HISTORY_WEEKS, 4)
        self.assertEqual(c.EMISSARY_POWER_HISTORY_LENGTH, 4 * 7 * 24)
        self.assertEqual(c.EMISSARY_POWER_RECALCULATE_STEPS, 672.0)
        self.assertEqual(c.EMISSARY_POWER_REDUCE_FRACTION, 0.9931704959660097)

        self.assertEqual(c.MAXIMUM_EMISSARY_HEALTH, 7)
