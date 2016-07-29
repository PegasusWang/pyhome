#!/usr/bin/env bash

curl --socks5 127.0.01:9050 http://checkip.amazonaws.com/
(echo authenticate '"rentonggeji"'; echo signal newnym; echo quit) | nc localhost 9051


sleep 3
curl --socks5 127.0.01:9050 http://checkip.amazonaws.com/
