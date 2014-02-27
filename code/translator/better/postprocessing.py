# -*- coding: utf-8 -*-
"""Defines postprocessing operations -- functions which operate on and
annotate candidate sentences.

Functions in this module are threaded together into a pipeline in
`translator.better.core`. They must satisfy a simple contract,
expressible with a simple type signature:

    postprocessor :: [(Sent, Ann)] -> [(Sent, Ann)]

That is, each postprocessor function accepts a list of `(sentence,
annotation)` tuples (where each `sentence` is a list of tokens and each
`annotation` is an arbitrary `dict` containing data about the
corresponding sentence) and returns a list of the same form, possibly
with fewer or more tuples and possibly with the given tuples modified in
some way."""


def pick_best_candidate(data):
    """The final postprocessing step which picks just one sentence from
    the candidate list."""

    # TODO: smarter selection!
    #
    # Right now we just pick the first element
    return (data and [data[0]]) or None
