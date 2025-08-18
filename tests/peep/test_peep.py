# SPDX-FileCopyrightText: 2022-present Claude
#
# SPDX-License-Identifier: MIT
import peep


def test_import():
    peep.broker = "localhost"
    assert True
