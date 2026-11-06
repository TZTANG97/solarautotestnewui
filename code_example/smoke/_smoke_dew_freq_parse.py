# -*- coding: utf-8 -*-
from dialogs.Dialog_thaiguodianyashanbian import parse_power_group_tree
from components.dewetron_autotest_panel import parse_power_group_tree as shared

assert parse_power_group_tree is shared
xml = (
    '<ChannelGroup Type="Power Groups">'
    '<Channel Name="POWER/0">'
    '<Channel Name="F_fund"/>'
    '<ChannelGroup Type="Voltage (U)">'
    '<ChannelGroup Type="Total RMS">'
    '<Channel Name="U1_tRMS"/>'
    "</ChannelGroup></ChannelGroup></Channel></ChannelGroup>"
)
tree = parse_power_group_tree(xml)
assert tree is not None
assert "F_fund" in tree["Frequency (F)"]["Fundamental"]
print("ok", sorted(tree.keys()))
