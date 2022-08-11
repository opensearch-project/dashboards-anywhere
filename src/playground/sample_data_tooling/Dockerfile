# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

FROM python:3

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN mkdir sample_data_tooling

COPY . sample_data_tooling