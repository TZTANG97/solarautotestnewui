import sys
sys.path.insert(0, '.')

# Test importing all dialogs
dialogs = [
    ('Dialog_thaioverloads', 'Ui_Dialog_thaioverloads'),
    ('Dialog_thaivoltprotect10min', 'Ui_Dialog_thaivoltprotect10min'),
    ('Dialog_thaizhiliufenliang', 'Ui_Dialog_thaizhiliufenliang'),
    ('Dialog_thaistaticmppttest', 'Ui_Dialog_thaistaticmppttest'),
    ('Dialog_thaicosPhi_Brazil', 'Ui_Dialog_thaicosPhi_Brazil'),
    ('Dialog_thaistaticQU', 'Ui_Dialog_thaiStaticQU'),
    ('Dialog_thaistaticcosPhi', 'Ui_Dialog_thaistaticcosPhi'),
    ('Dialog_thaixiebodianliu', 'Ui_Dialog_thaixiebodianliu'),
    ('Dialog_thaiguoqianpin_immun', 'Ui_Dialog_thaiguoqianpin_immun'),
    ('Dialog_thaiguoqianya_pin', 'Ui_Dialog_thaiguoqianya_pin'),
    ('Dialog_thaitestPU', 'Ui_Dialog_thaitestPU'),
    ('Dialog_thaiguopinjiangzai', 'Ui_Dialog_thaiguopinjiangzai'),
    ('Dialog_thaifrequencyadaptability', 'Ui_Dialog_thaifrequencyadaptability'),
    ('Dialog_thaichonglian', 'Ui_Dialog_thaichonglian'),
    ('Dialog_thaiWT3000E', 'Ui_Dialog_thai_WT3000E'),
    ('Dialog_thaiWT1806E', 'Ui_Dialog_thai_WT1806E'),
    ('Dialog_thaiWT1800', 'Ui_Dialog_thai_WT1800'),
    ('Dialog_thaiWT5000', 'Ui_Dialog_thai_WT5000'),
    ('Dialog_thaiWT3000_Setting', 'Ui_Dialog_thai_WT3000_Setting'),
]

for mod_name, class_name in dialogs:
    try:
        mod = __import__(mod_name, fromlist=[class_name])
        cls = getattr(mod, class_name)
        print(f'[OK] {mod_name}.{class_name}')
    except Exception as e:
        print(f'[FAIL] {mod_name}: {e}')

print('\nAll imports done')
