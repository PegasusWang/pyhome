#!/usr/bin/env bash

(echo authenticate '"rentonggeji"'; echo signal newnym; echo quit) | nc localhost 9051
