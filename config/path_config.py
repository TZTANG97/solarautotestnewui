from .app_config import config

PATH_WT_EXE = config.get('PATH', 'wt_exe')
PATH_RECORDINGS = {
    'WT3000': config.get('PATH', 'recordings_wt3000'),
    'WT1800': config.get('PATH', 'recordings_wt1800'),
    'WT1806E': config.get('PATH', 'recordings_wt1806e'),
    'WT5000': config.get('PATH', 'recordings_wt5000')
}
