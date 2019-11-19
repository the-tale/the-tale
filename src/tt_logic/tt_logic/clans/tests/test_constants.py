

import unittest

from .. import constants as c


class ConstantsTest(unittest.TestCase):

    def test_constants_values(self):

        self.assertEqual(c.EXPECTED_EVENT_LENGTH, 7)
        self.assertEqual(c.MAX_EVENT_LENGTH, 30)

        self.assertEqual(c.EMISSARY_RECEIVE_PERIOD_FOR_NEW_CLAN, 21)
        self.assertEqual(c.EXPECTED_EMISSARY_RECEIVE_PERIOD_FOR_TOP_CLAN, 7)

        self.assertEqual(c.SIMULTANEOUS_EMISSARY_EVENTS, 2)
        # self.assertEqual(c.SIMULTANEOUS_EMISSARY_EVENTS_DELTA, 1)

        # self.assertGreaterOrEqueal(c.SIMULTANEOUS_EMISSARY_EVENTS - c.SIMULTANEOUS_EMISSARY_EVENTS_DELTA, 1)

        self.assertEqual(c.INITIAL_POINTS_IN_DAY, 1000)

        self.assertEqual(c.PRICE_START_EVENT, 1000)
        self.assertEqual(c.PRICE_CREATE_EMISSARY, 18000)
        self.assertEqual(c.PRICE_MOVE_EMISSARY, 1000)
        self.assertEqual(c.PRICE_DISMISS_EMISSARY, 1000)

        self.assertEqual(c.PRICE_START_EVENT_DELTA, 0.15)

        self.assertEqual(c.TOP_CARD_POINTS_BONUS, 100)

        self.assertEqual(c.INITIAL_MEMBERS_MAXIMUM, 5)
        self.assertEqual(c.INITIAL_EMISSARY_MAXIMUM, 2)
        self.assertEqual(c.INITIAL_FREE_QUESTS_MAXIMUM, 2)
        self.assertEqual(c.INITIAL_POINTS_GAIN, 857)
        self.assertEqual(c.INITIAL_POINTS, 19000)
        self.assertEqual(c.INITIAL_FREE_QUESTS, 2)

        self.assertEqual(c.MAXIMUM_POINTS_GAIN, 2571)
        self.assertEqual(c.MAXIMUM_EMISSARIES, 10)
        self.assertEqual(c.MEMBERS_TO_EMISSARY, 5)

        self.assertEqual(c.MAXIMUM_MEMBERS, 50)

        self.assertEqual(c.MAXIMUM_FREE_QUESTS, 10)

        self.assertEqual(c.MAXIMUM_POINTS, 36000)

        self.assertEqual(c.EMISSARY_MAXIMUM_LEVEL_STEPS, 8)
        self.assertEqual(c.POINTS_GAIN_LEVEL_STEPS, 20)
        self.assertEqual(c.MEMBERS_MAXIMUM_LEVEL_STEPS, 45)

        self.assertEqual(c.EXPECTED_LEVELING_TIME, 5 * 365)

        self.assertEqual(c.POINTS_GAIN_INCREMENT_ON_LEVEL_UP, 85)

        self.assertEqual(c.EXPERIENCE_IN_DAY_ON_START, 4000)
        self.assertEqual(c.EXPERIENCE_IN_DAY_ON_END, 20000)

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
                          3.2840292365290225,
                          3.5949493421257985,
                          3.935306247793965,
                          4.307886924150236,
                          4.715742202190153,
                          5.1622117546420725,
                          5.650951442466117,
                          6.185963250421527,
                          6.771628056826133,
                          7.412741505839078,
                          8.114553276002567,
                          8.882810066588263,
                          9.723802653736723,
                          10.644417401703297,
                          11.652192651003974,
                          12.755380445188557,
                          13.963014101683264,
                          15.284982179998288,
                          16.73210945297983,
                          18.316245544129796,
                          20.050361956788898,
                          21.948658289694666,
                          24.026678508647457,
                          26.301438226360595,
                          28.791564032710077,
                          31.517446016272444,
                          34.50140472605462,
                          37.76787394056133,
                          41.343600740781994,
                          45.25786452537034,
                          49.54271676139529,
                          54.23324343383287,
                          59.36785234283425,
                          64.98858760126856,
                          71.1414739077645,
                          77.87689341428842,
                          85.24999827419254,
                          93.32116224883234,
                          102.15647507067797,
                          111.82828361095156,
                          122.41578428307474,
                          134.00567153274915,
                          146.69284772475106,
                          160.5812002392608])

        self.assertEqual(c.EXPERIENCE_PER_EVENT, 1000)

        self.assertEqual(c.EMISSARY_MEXIMUM_LEVELS_EXPERIENCE,
                         [28600,
                          50500,
                          91900,
                          174800,
                          351300,
                          752000,
                          1714800,
                          4136000])

        self.assertEqual(c.POINTS_GAIN_LEVELS_EXPERIENCE,
                         [28600,
                          34100,
                          40800,
                          48900,
                          58900,
                          71300,
                          86600,
                          105600,
                          129300,
                          158900,
                          196100,
                          242800,
                          301700,
                          376200,
                          470500,
                          590200,
                          742300,
                          936000,
                          1182900,
                          1498300])

        self.assertEqual(c.FREE_QUESTS_MAXIMUM_LEVELS_EXPERIENCE,
                         [28600,
                          50500,
                          91900,
                          174800,
                          351300,
                          752000,
                          1714800,
                          4136000])

        self.assertEqual(c.MEMBERS_MAXIMUM_LEVELS_EXPERIENCE,
                         [12000,
                          13300,
                          14600,
                          16100,
                          17800,
                          19700,
                          21800,
                          24100,
                          26700,
                          29700,
                          32900,
                          36600,
                          40700,
                          45400,
                          50600,
                          56500,
                          63300,
                          70900,
                          79600,
                          89400,
                          100700,
                          113600,
                          128400,
                          145400,
                          165000,
                          187600,
                          213700,
                          243900,
                          278900,
                          319700,
                          367100,
                          422500,
                          487100,
                          562800,
                          651500,
                          755700,
                          878100,
                          1022200,
                          1192000,
                          1392400,
                          1629100,
                          1909000,
                          2240400,
                          2633000,
                         3098600])
