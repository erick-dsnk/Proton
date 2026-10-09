# ICMP ECHO requests (ping)

This upstream Proton networking guide is retained for the experimental open
source [Proton Vanguard compatibility effort](README.md), which aims to bring
League of Legends back to Linux. Enabling ping only changes ICMP availability;
it provides no evidence of Vanguard acceptance or playable League. Record the
host configuration with any results using the [testing requirements](TESTING.md).

Some games rely on ICMP ECHO requests to detect network connectivity,
or to measure connection ping.

Proton supports sending ICMP ECHO requests using RAW sockets or DGRAM
ICMP sockets, but the former requires elevated privileges, and the
latter may also be disabled by default.

DGRAM ICMP sockets can be enabled for a given set of user groups by
running the following command, and will stay enabled until next reboot:

```
sudo sysctl -w net.ipv4.ping_group_range="<low> <high>"
```

Where <low> (resp <high>) is lower bound (resp higher) of the user
groups which will be allowed to create such sockets. It is possible to
enable them for any group by using "0 4294967295".

In order for the configuration to be persistent, it is possible to add
the following line to `/etc/sysctl.conf` (or a file in `/etc/sysctl.d`):

```
net.ipv4.ping_group_range="<low> <high>"
```
