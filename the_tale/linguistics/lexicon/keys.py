# coding: utf-8
import os

from rels import Column
from rels import Enum

from dext.common.utils import discovering


def get_key_records():
    CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
    GROUPS_DIR = os.path.join(CURRENT_DIR, 'groups')

    keys = []

    for module in discovering.discover_modules_in_directory(GROUPS_DIR, 'the_tale.linguistics.lexicon.groups'):
        keys.extend(getattr(module, 'KEYS', ()))

    return keys


class LEXICON_KEY(Enum):
    text = Column(unique=False)
    group = Column(unique=False)
    description = Column(unique=False)
    variables = Column(unique=False, no_index=True)

    records = get_key_records()
