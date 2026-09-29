# -*- coding: utf-8 -*-
from pathlib import Path


def patch_build() -> None:
    p = Path(r"E:\solarautotestnewui\packaging\Build-ReleasePackage.ps1")
    t = p.read_text(encoding="utf-8")
    if "Install-PathHelpers.ps1" in t:
        print("build already has helpers")
        return
    old = (
        "$ps1Files = @(\n"
        '    "Install-SolarAutoTest.ps1",\n'
        '    "Check-And-Update.ps1",\n'
        '    "Verify-Install.ps1"\n'
        ")"
    )
    new = (
        "$ps1Files = @(\n"
        '    "Install-SolarAutoTest.ps1",\n'
        '    "Install-PathHelpers.ps1",\n'
        '    "Check-And-Update.ps1",\n'
        '    "Verify-Install.ps1"\n'
        ")"
    )
    if old not in t:
        raise SystemExit("build ps1Files missing")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")
    print("build patched")


def patch_check() -> None:
    p = Path(r"E:\solarautotestnewui\packaging\Check-And-Update.ps1")
    t = p.read_text(encoding="utf-8")
    old = (
        '        "-InstallDir", $InstallDir,\n'
        '        "-SkipVerify"\n'
    )
    new = (
        '        "-InstallDir", $InstallDir,\n'
        '        "-Quiet",\n'
        '        "-SkipVerify"\n'
    )
    idx = t.find('"-InstallDir", $InstallDir')
    if idx < 0:
        raise SystemExit("check InstallDir missing")
    window = t[idx : idx + 120]
    if '"-Quiet"' in window:
        print("check already quiet")
        return
    if old not in t:
        raise SystemExit("check args missing")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")
    print("check patched")


def write_paths_example() -> None:
    p = Path(r"E:\solarautotestnewui\config_files\paths.ini.example")
    p.write_text(
        "[paths]\n"
        "# Prefer non-system drive on lab PCs, e.g. D:\\SolarAutoTest\\data\n"
        "data_root = auto\n"
        "runtime_root = auto\n"
        "\n"
        "# Or set env:\n"
        "#   SOLARAUTOTEST_DATA=D:\\SolarData\n"
        "#   SOLARAUTOTEST_RUNTIME=D:\\SolarRuntime\n",
        encoding="utf-8",
    )
    print("paths example written")


def patch_config_ini() -> None:
    p = Path(r"E:\solarautotestnewui\config_files\config.ini")
    t = p.read_text(encoding="utf-8")
    if "data_root" in t:
        print("config already has data_root")
        return
    needle = "wt_file_save_path = auto\n"
    insert = (
        "wt_file_save_path = auto\n"
        "# Optional roots (also config_files/paths.ini). auto = resolve via utils/app_paths.py\n"
        "# data_root = D:/SolarAutoTest/data\n"
        "# runtime_root = D:/SolarAutoTest/runtime\n"
    )
    if needle not in t:
        raise SystemExit("config needle missing")
    p.write_text(t.replace(needle, insert, 1), encoding="utf-8")
    print("config.ini annotated")


def patch_install_txt() -> None:
    p = Path(r"E:\solarautotestnewui\packaging\INSTALL.txt")
    t = p.read_text(encoding="utf-8")
    if "Choose install locations" in t or "data_root" in t and "Install steps" in t:
        # still update folders section
        pass
    old = (
        "Install steps (first time)\n"
        "--------------------------\n"
        "1. Unzip SolarAutoTest-Setup-YYYYMMDD.zip to a local folder.\n"
        "2. Double-click install.bat\n"
        "3. Wait for copy + uv sync + verify\n"
        "4. Edit %LOCALAPPDATA%\\SolarAutoTest\\config_files\\config.ini  [update] section\n"
        "   (see Aliyun / LAN channel below)\n"
        "5. Use desktop shortcut \"SolarAutoTest\"\n"
    )
    new = (
        "Install steps (first time)\n"
        "--------------------------\n"
        "1. Unzip SolarAutoTest-Setup-YYYYMMDD.zip to a local folder.\n"
        "2. Double-click install.bat\n"
        "3. Choose install / data / runtime directories when prompted\n"
        "   (Enter=default; type a path; or B=browse). Prefer D:/E: if available.\n"
        "4. Wait for copy + uv sync + verify\n"
        "5. Edit <InstallDir>\\config_files\\config.ini  [update] section\n"
        "   (see Aliyun / LAN channel below)\n"
        "6. Use desktop shortcut \"SolarAutoTest\"\n"
    )
    if old in t:
        t = t.replace(old, new, 1)
        print("install steps updated")
    else:
        print("install steps pattern skipped")

    old_folders = (
        "Folders\n"
        "-------\n"
        "- App:     %LOCALAPPDATA%\\SolarAutoTest\n"
        "- Runtime: %LOCALAPPDATA%\\SolarAutoTestRuntime\n"
        "- Version: %LOCALAPPDATA%\\SolarAutoTest\\VERSION\n"
    )
    new_folders = (
        "Folders\n"
        "-------\n"
        "- App:     chosen at install (default prefers D:\\SolarAutoTest if D: exists,\n"
        "           else %LOCALAPPDATA%\\SolarAutoTest)\n"
        "- Data:    <InstallDir>\\data  or config_files\\paths.ini data_root=\n"
        "- Runtime: <InstallDir>\\runtime or runtime_root.txt (venv / uv cache)\n"
        "- Version: <InstallDir>\\VERSION\n"
        "\n"
        "Change disks later\n"
        "------------------\n"
        "1. Re-run install.bat and pick new folders, or\n"
        "2. Edit <InstallDir>\\config_files\\paths.ini and runtime_root.txt, then restart.\n"
        "Env overrides: SOLARAUTOTEST_DATA / SOLARAUTOTEST_RUNTIME / SOLARAUTOTEST_HOME\n"
    )
    if old_folders in t:
        t = t.replace(old_folders, new_folders, 1)
        print("folders updated")
    else:
        print("folders pattern skipped")
    p.write_text(t, encoding="utf-8")


def patch_install_bat() -> None:
    p = Path(r"E:\solarautotestnewui\packaging\install.bat")
    t = p.read_text(encoding="utf-8")
    if "Choose install" in t:
        print("install.bat already notes paths")
        return
    old = (
        "echo ============================================================\n"
        "echo  SolarAutoTest Installer\n"
        "echo ============================================================\n"
        "echo.\n"
    )
    new = (
        "echo ============================================================\n"
        "echo  SolarAutoTest Installer\n"
        "echo ============================================================\n"
        "echo  You can choose App / Data / Runtime folders (not only C:).\n"
        "echo  Tip: install.bat -InstallDir D:\\SolarAutoTest -Quiet\n"
        "echo.\n"
    )
    if old not in t:
        raise SystemExit("install.bat header missing")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")
    print("install.bat patched")


def write_tests() -> None:
    p = Path(r"E:\solarautotestnewui\tests\test_app_paths.py")
    p.write_text(
        '''# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def test_data_root_env_override(monkeypatch, tmp_path):
    from utils import app_paths

    app_paths.clear_path_cache()
    monkeypatch.setenv("SOLARAUTOTEST_DATA", str(tmp_path / "data"))
    monkeypatch.delenv("SOLARAUTOTEST_RUNTIME", raising=False)
    got = app_paths.data_root(force_reload=True)
    assert Path(got) == (tmp_path / "data").resolve()
    assert Path(got).is_dir()


def test_data_subdir_and_runtime(monkeypatch, tmp_path):
    from utils import app_paths

    app_paths.clear_path_cache()
    monkeypatch.setenv("SOLARAUTOTEST_DATA", str(tmp_path / "data"))
    monkeypatch.setenv("SOLARAUTOTEST_RUNTIME", str(tmp_path / "rt"))
    sub = app_paths.data_subdir("command_save_files", "dewetron_presets")
    assert Path(sub).is_dir()
    assert Path(sub).name == "dewetron_presets"
    rt = app_paths.runtime_root(force_reload=True)
    assert Path(rt) == (tmp_path / "rt").resolve()


def test_paths_ini_in_home(monkeypatch, tmp_path):
    from utils import app_paths

    app_paths.clear_path_cache()
    monkeypatch.delenv("SOLARAUTOTEST_DATA", raising=False)
    monkeypatch.delenv("SOLARAUTOTEST_RUNTIME", raising=False)
    home = tmp_path / "install"
    cfg = home / "config_files"
    cfg.mkdir(parents=True)
    (cfg / "paths.ini").write_text(
        "[paths]\ndata_root = {}\nruntime_root = {}\n".format(
            tmp_path / "ini_data", tmp_path / "ini_rt"
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("SOLARAUTOTEST_HOME", str(home))
    assert Path(app_paths.data_root(force_reload=True)) == (tmp_path / "ini_data").resolve()
    assert Path(app_paths.runtime_root(force_reload=True)) == (tmp_path / "ini_rt").resolve()
''',
        encoding="utf-8",
    )
    print("tests written")


if __name__ == "__main__":
    patch_build()
    patch_check()
    write_paths_example()
    patch_config_ini()
    patch_install_txt()
    patch_install_bat()
    write_tests()
