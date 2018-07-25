# -*- coding: utf-8 -*-

"""
This file is part of the Reset Card Scheduling add-on for Anki.

Main Module, hooks add-on methods into Anki.

Copyright: (c) 2015-2015 Jeff Baitis <jeff@baitis.net>
           (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

from aqt.qt import *
from aqt import mw
from aqt.utils import askUser, tooltip
from aqt.browser import Browser
from anki.hooks import addHook

from .consts import anki21

# Col is a collection of cards, cids are the ids of the cards to reset.
def resetSelectedCardScheduling(cids):
    """
    Resets statistics for selected cards,
    and removes them from learning queues.
    """
    # Removes card from dynamic deck
    mw.col.sched.remFromDyn(cids)
    # Resets selected cards in current collection
    mw.col.sched.resetCards(cids)
    # Removes card from learning queues
    mw.col.sched.removeLrn(cids)


def onBrowserResetCards(self):
    cids = self.selectedCards()
    if not cids:
        tooltip("No cards selected.")
        return
    r = askUser("This will reset <b>ALL</b> the scheduling information and "
                "progress of <b>{}</b> selected cards."
                "<br><br>Are you sure you want to proceed?".format(len(cids)),
                defaultno=True, title="Reset Card Scheduling")
    if not r:
        return
    self.model.beginReset()
    self.mw.checkpoint(_("Reset scheduling and learning on selected cards"))

    resetSelectedCardScheduling(cids)

    self.model.endReset()
    self.mw.reset()

    tooltip("{} cards reset.".format(len(cids)), parent=self)


def onDeckBrowserResetCards(did):
    if mw.col.decks.isDyn(did):
        tooltip("Can't reset scheduling for filtered/custom decks.")
    deck_name = mw.col.decks.name(did)
    cids = mw.col.decks.cids(did, children=True)
    if not cids:
        tooltip("Deck contains no cards.")
        return
    r = askUser("This will reset <b>ALL</b> scheduling information and "
                "progress in the deck '{}' and all of its subdecks ({} cards)."
                "<br><br>Are you sure you want to proceed?".format(deck_name,
                                                                   len(cids)),
                defaultno=True, title="Reset Card Scheduling")
    if not r:
        return
    mw.checkpoint("Reset selected deck")
    mw.progress.start()

    resetSelectedCardScheduling(cids)

    mw.progress.finish()
    mw.reset()

    tooltip("{} card(s) reset.".format(len(cids)), parent=mw)


def onBrowserSetupMenus(self):
    if anki21:
        menu = self.form.menu_Cards
    else:
        menu = self.form.menuEdit
    a = menu.addAction("Reset selected cards")
    a.triggered.connect(self.onBrowserResetCards)


def onDeckBrowserShowOptions(menu, did):
    a = menu.addAction("Reset deck")
    a.triggered.connect(lambda _, did=did: onDeckBrowserResetCards(did))


# Hooks

Browser.onBrowserResetCards = onBrowserResetCards
addHook('browser.setupMenus', onBrowserSetupMenus)
addHook('showDeckOptions', onDeckBrowserShowOptions)
