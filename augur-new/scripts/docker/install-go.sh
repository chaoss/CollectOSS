#!/bin/bash
# install Go
installGo() (
    cd "$(mktemp -d)"
    wget https://golang.org/dl/go1.16.5.linux-amd64.tar.gz
    rm -rf /usr/local/go && tar -C /usr/local -xzf go1.16.5.linux-amd64.tar.gz
)
installGo
export PATH=$PATH:/usr/local/go/bin