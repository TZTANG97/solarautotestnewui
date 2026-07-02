# -*- coding: utf-8 -*-
import re

with open('config_files/dewetron.xml', 'r', encoding='utf-8') as f:
    xml = f.read()

# Check U1_tRMS (checked) vs U2_tRMS (unchecked) - compare ALL properties
for ch_name in ['U1_tRMS', 'U2_tRMS']:
    print(f"\n{'='*60}")
    print(f"=== {ch_name} ===")

    # Find CalculatedSource
    idx = xml.find(f'ShortId"><StringValue>"{ch_name}"')
    if idx > 0:
        cs_start = xml.rfind('<CalculatedSource', 0, idx)
        cs_end = xml.find('</CalculatedSource>', idx)
        if cs_start > 0 and cs_end > 0:
            cs_end += len('</CalculatedSource>')
            cs_xml = xml[cs_start:cs_end]
            print(f"\n--- CalculatedSource ---")
            print(cs_xml)

        # Find NeonConfig
        nc_start = xml.find('<ChainElement name="NeonConfig"', idx)
        if nc_start > 0:
            nc_end = xml.find('</ChainElement>', nc_start)
            if nc_end > 0:
                nc_end += len('</ChainElement>')
                nc_xml = xml[nc_start:nc_end]
                print(f"\n--- NeonConfig ---")
                print(nc_xml)
