from PyQt5 import QtWidgets
import sys
app = QtWidgets.QApplication(sys.argv)

# Test importing all dialogs
from dialogs.Dialog_thaioverloads import Ui_Dialog_thaioverloads
from dialogs.Dialog_thaivoltprotect10min import Ui_Dialog_thaivoltprotect10min
from dialogs.Dialog_thaizhiliufenliang import Ui_Dialog_thaizhiliufenliang
from dialogs.Dialog_thaistaticmppttest import Ui_Dialog_thaistaticmppttest
from dialogs.Dialog_thaicosPhi_Brazil import Ui_Dialog_thaicosPhi_Brazil
from dialogs.Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU as Ui_Dialog_thaistaticQU
from dialogs.Dialog_thaistaticcosPhi import Ui_Dialog_thaistaticcosPhi
from dialogs.Dialog_thaixiebodianliu import Ui_Dialog_thaixiebodianliu
from dialogs.Dialog_thaiguoqianpin_immun import Ui_Dialog_thaiguoqianpin_immun
from dialogs.Dialog_thaiguoqianya_pin import Ui_Dialog_thaiguoqianya_pin
from dialogs.Dialog_thaitestPU import Ui_Dialog_thaitestPU
from dialogs.Dialog_thaiguopinjiangzai import Ui_Dialog_thaiguopinjiangzai
from dialogs.Dialog_thaifrequencyadaptability import Ui_Dialog_thaifrequencyadaptability
from dialogs.Dialog_thaichonglian import Ui_Dialog_thaichonglian
from dialogs.Dialog_thaiWT3000E import Ui_Dialog_thai_WT3000E
from dialogs.Dialog_thaiWT1806E import Ui_Dialog_thai_WT1806E
from dialogs.Dialog_thaiWT1800 import Ui_Dialog_thai_WT1800
from dialogs.Dialog_thaiWT5000 import Ui_Dialog_thai_WT5000
from dialogs.Dialog_thaiWT3000_Setting import Ui_Dialog_thai_WT3000_Setting
print('All imports OK')

# Test creating each dialog
dialogs = [
    ('overloads', Ui_Dialog_thaioverloads),
    ('voltprotect10min', Ui_Dialog_thaivoltprotect10min),
    ('zhiliufenliang', Ui_Dialog_thaizhiliufenliang),
    ('staticmppttest', Ui_Dialog_thaistaticmppttest),
    ('cosPhi_Brazil', Ui_Dialog_thaicosPhi_Brazil),
    ('staticQU', Ui_Dialog_thaistaticQU),
    ('staticcosPhi', Ui_Dialog_thaistaticcosPhi),
    ('xiebodianliu', Ui_Dialog_thaixiebodianliu),
    ('guoqianpin_immun', Ui_Dialog_thaiguoqianpin_immun),
    ('guoqianya_pin', Ui_Dialog_thaiguoqianya_pin),
    ('testPU', Ui_Dialog_thaitestPU),
    ('guopinjiangzai', Ui_Dialog_thaiguopinjiangzai),
    ('frequencyadaptability', Ui_Dialog_thaifrequencyadaptability),
    ('chonglian', Ui_Dialog_thaichonglian),
    ('WT3000E', Ui_Dialog_thai_WT3000E),
    ('WT1806E', Ui_Dialog_thai_WT1806E),
    ('WT1800', Ui_Dialog_thai_WT1800),
    ('WT5000', Ui_Dialog_thai_WT5000),
    ('WT3000_Setting', Ui_Dialog_thai_WT3000_Setting),
]

for name, cls in dialogs:
    try:
        w = QtWidgets.QMainWindow()
        ui = cls()
        ui.setupUi(w)
        print(f'[OK] {name}')
    except Exception as e:
        print(f'[FAIL] {name}: {e}')

print('\nAll done')
