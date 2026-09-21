import re
xml = open('config_files/dewetron.xml', 'r', encoding='utf-8').read()
xml = xml[xml.find('<?xml'):]

# Check AI 1/U1 ShortId distance to Used/Neon
m = re.search(r'ShortId"><StringValue>"AI 1/U1"', xml)
if m:
    print(f'ShortId AI 1/U1 at position {m.start()}')
    # Search backward 5000 chars for Used
    start_search = max(0, m.start() - 5000)
    before = xml[start_search:m.start()]
    used_m = re.search(r'<Property name="Used"><BooleanValue>(True|False)</BooleanValue>', before)
    if used_m:
        dist = len(before) - used_m.start()
        print(f'  Used found: {dist} chars before ShortId (value={used_m.group(1)})')
    else:
        print(f'  Used NOT found in {5000} chars before ShortId')
    # Search forward 6000 chars for Neon/Active
    after = xml[m.start():min(len(xml), m.start() + 6000)]
    neon_m = re.search(r'<Property name="Neon/Active"><BooleanValue>(True|False)</BooleanValue>', after)
    if neon_m:
        print(f'  Neon/Active found: {neon_m.start()} chars after ShortId (value={neon_m.group(1)})')
    else:
        print(f'  Neon/Active NOT found in 6000 chars after ShortId')
else:
    print('AI 1/U1 ShortId NOT found')

# Check all AI channels
print()
print('=== All AI ShortIds ===')
for m2 in re.finditer(r'ShortId"><StringValue>"(AI [^"]+)"', xml):
    print(f'  {m2.group(1)} at position {m2.start()}')

# Check InputChannels
print()
print('=== InputChannels ===')
for m3 in re.finditer(r'POWER/InputChannels/([A-Z]+\d+)"><ChannelID>(\d+)</ChannelID>', xml):
    slot = m3.group(1)
    ch_id = int(m3.group(2))
    if ch_id == 18446744073709551615:
        name = 'UNUSED'
    else:
        # Find the ShortId for this channel ID
        ch_m = re.search(rf'<Channel id="{ch_id}">(.*?)</Channel>', xml, re.DOTALL)
        if ch_m:
            sid = re.search(r'ShortId"><StringValue>"([^"]+)"', ch_m.group(1))
            name = sid.group(1) if sid else f'Unknown({ch_id})'
        else:
            name = f'Unknown({ch_id})'
    print(f'  {slot} -> {name} (ID={ch_id})')

# Check LineToLineVoltageInput
lltvi = re.search(r'POWER/LineToLineVoltageInput.*?<BooleanValue>([^<]+)', xml)
print(f'\nLineToLineVoltageInput = {lltvi.group(1) if lltvi else "Not found"}')

# Check WiringType
wiring = re.search(r'POWER/WiringType.*?enum="PowerWiringType">([^<]+)', xml)
print(f'WiringType = {wiring.group(1) if wiring else "Not found"}')
