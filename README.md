# procurve-sdn

This is an experiment in delaratively configuring an HP 1800-24g J9028B "smart" switch using selenium.

I created this because i always find myself second-guessing things like "did i actually enable lacp on _all_ the ports?" or "did i remember to delete those vlans i was messing with?".

Declarative, idempotent configuration solves this annoyance for good.

Currently this knows how to enforce jumbo frames and lacp on all ports.

Future goals involve feeding some sort of config file for per-port vlan configuration.
