# coding: utf-8

from dext.utils.app_settings import app_settings

bills_settings = app_settings('POLITICS',
                              RATIONALE_MIN_LENGTH=100,
                              VOTES_FOR_CONFIRM_PROPOSAL=2,
                              VOTES_FOR_ACCEPT_BILL_PERCENT=0.6,
                              PROPOSAL_LIVE_TIME = 4*24*60*60,
                              VOTING_LIVE_TIME = 4*24*60*60,
                              FORUM_PROPOSAL_CATEGORY_SLUG='politic-proposals',
                              FORUM_VOTING_CATEGORY_SLUG='politic-votings',
                              BILLS_ON_PAGE=10)
