# SPDX-FileCopyrightText: 2022-present Claude
#
# SPDX-License-Identifier: MIT


class IBackend:
    def run(self):
        raise NotImplementedError

    def publish_results(self, counts, lux):
        raise NotImplementedError
