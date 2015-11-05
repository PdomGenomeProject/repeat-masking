#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2012-2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2012-2015   Indiana University
#
# This file is part of the Polistes dominula genome project and is licensed
# under the Creative Commons Attribution 4.0 International License.
# -----------------------------------------------------------------------------
import re, string, sys

for line in sys.stdin:
  line = line.rstrip()
  if not line.startswith(">"):
    line = re.sub('[a-z]', 'N', line)
  print line
