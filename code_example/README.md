# code_example — 一次性脚本分筐

正式业务代码不放这里。按类型进子目录，避免根下上百个 `_*.py` 平铺。

| 目录 | 放 |
|------|----|
| `patches/` | `_patch_*` `_align_*` `_gen_*` `_rename_*` `_enrich_*` `_fix_*` `_add_*` |
| `audits/` | `_audit_*` `_peek_*` `_scan_*` `_check_*` `_verify_*` `_dump_*` `_inspect_*` 以及 `*_audit.txt` / `*_dump.txt` |
| `smoke/` | `_smoke_*`、非正式 `_test_*` |
| `ops/` | 周报、路径同步、安装辅助 `*.ps1` |
| `media/` | 样例媒体 / CSV |
| `update_e2e/` | E2E 更新 |

未归入上表、仍有复用价值的具名脚本可暂时留在本目录根下，整理时再挪。
