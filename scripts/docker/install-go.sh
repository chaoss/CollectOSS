#!/bin/bash

export VERSION="1.22.9"

cd "$(mktemp -d)"
wget https://golang.org/dl/go${VERSION}.linux-amd64.tar.gz
rm -rf /usr/local/go && tar -C /usr/local -xzf go${VERSION}.linux-amd64.tar.gz

export PATH=$PATH:/usr/local/go/bin
