import re
xml = open('config_files/dewetron.xml', 'r', encoding='utf-8').read()
xml = xml[xml.find('<?xml'):]

# 1. 解析所有 Channel 的 id -> ShortId 映射
id_to_short = {}
# 找到所有 <Channel id="xxx"> 到下一个 </Channel> 之间的内容
for m in re.finditer(r'<Channel id="(\d+)">(.*?)</Channel>', xml, re.DOTALL):
    ch_id = int(m.group(1))
    body = m.group(2)
    sid_m = re.search(r'ShortId"><StringValue>"([^"]+)"', body)
    if sid_m:
        id_to_short[ch_id] = sid_m.group(1)

# 2. 找到 InputChannels 映射
print('=== InputChannels Mapping ===')
for m in re.finditer(r'POWER/InputChannels/([A-Z]+\d+)"><ChannelID>(\d+)</ChannelID>', xml):
    slot = m.group(1)
    ch_id = int(m.group(2))
    if ch_id == 18446744073709551615:
        name = 'UNUSED'
    else:
        name = id_to_short.get(ch_id, f'Unknown({ch_id})')
    print(f'  {slot} -> {name} (ID={ch_id})')

# 3. 打印 AI 通道的 ID 映射
print()
print('=== AI Channel ID Mapping ===')
for cid, sid in sorted(id_to_short.items()):
    if sid.startswith('AI'):
        print(f'  {sid} -> ID={cid}')
