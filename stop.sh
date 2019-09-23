#!/bin/sh
ps wx | grep "[p]ython3 -u whatsappwebbot.py" | awk '{print $1}' | xargs kill
