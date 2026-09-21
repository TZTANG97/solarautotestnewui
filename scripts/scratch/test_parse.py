# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Dialog_thaiguodianyashanbian import parse_power_group_tree

with open('config_files/dewetron.xml', 'r', encoding='utf-8') as f:
    xml = f.read()

tree = parse_power_group_tree(xml)
if tree:
    for cat, subs in tree.items():
        total = sum(len(chs) for chs in subs.values())
        print(f"\n{cat}: ({total} channels)")
        for sub_name, channels in subs.items():
            print(f"  {sub_name}: {len(channels)} channels")
            for ch in channels[:3]:
                print(f"    {ch}")
            if len(channels) > 3:
                print(f"    ... +{len(channels)-3} more")
else:
    print("parse_power_group_tree returned None")
