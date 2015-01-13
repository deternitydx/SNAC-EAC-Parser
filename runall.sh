#!/bin/bash

cat ../../allDocsList.txt | parallel --pipe -j4 python generate_triples.py > ../../allTriples.ttl
