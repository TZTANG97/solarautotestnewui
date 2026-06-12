import sys, time
sys.path.insert(0, '.')
from PyQt5 import QtWidgets
from app.context import AppContext
app = QtWidgets.QApplication(sys.argv)
app_ctx = AppContext()

from setup.main_setup import initialize_setup_windows
t0 = time.time()
setup_windows = initialize_setup_windows(app_ctx)
t1 = time.time()
print('[TIME] initialize_windows took %.2fs' % (t1-t0))

lazy = setup_windows['dialog_window']
print('[TYPE] dialog_window: %s' % type(lazy).__name__)
print('[ATTR] has .show: %s' % hasattr(lazy, 'show'))

t2 = time.time()
lazy.show()
t3 = time.time()
print('[TIME] first .show() took %.2fs' % (t3-t2))

t4 = time.time()
lazy.hide()
t5 = time.time()
print('[TIME] second .hide() took %.4fs' % (t5-t4))

ui_lazy = setup_windows['uithaichonglian']
print('[TYPE] uithaichonglian: %s' % type(ui_lazy).__name__)
t6 = time.time()
_ = ui_lazy.pushButton_TestAppend
t7 = time.time()
print('[TIME] UI attr access took %.4fs' % (t7-t6))
print('[OK] lazy loading works')
