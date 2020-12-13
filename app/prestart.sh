#!/bin/bash
if [ -f /recoll.conf ]; then
	mv -n /recoll.conf /root/.recoll/
fi
