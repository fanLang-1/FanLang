# -*- coding: utf-8 -*-
"""
凡语 FanLang — 发布自动化中间层.

这个脚本封装了所有你需要理解的 DevOps 操作：
  - git add / commit / push
  - pip 包构建
  - PyPI 发布
  - 博客格式转换

你只需要：
  1. 把 PyPI token 填进配置文件
  2. 双击 publish.bat
  3. 选数字
"""
from __future__ import annotations

import os
import sys
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_FILE = ROOT / ".fanlang.json"
PYPI_REPO = "https://upload.pypi.org/legacy/"

# ── 配置 ────────────────────────────────────────────
CONFIG_TEMPLATE = {
    "pypi_token": "",          # 从 https://pypi.org/manage/account/token/ 生成
    "pypi_username": "__token__",
    "git_remote": "https://gitcode.com/desshu/FanLang.git",
    "packages": ["fanlang", "fanlang-streamlit", "fanlang-langchain"],
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {}


def save_config(config: dict):
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


# ── 工具函数 ─────────────────────────────────────────
def run(cmd: str, cwd: Path | None = None) -> tuple[int, str]:
    """执行终端命令，返回 (exit_code, output)."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=str(cwd) if cwd else None,
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        return result.returncode, (result.stdout + result.stderr).strip()
    except Exception as e:
        return 1, str(e)


def heading(text: str):
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}")


def success(text: str):
    print(f"  ✓ {text}")


def fail(text: str):
    print(f"  ✗ {text}")


# ── 操作 1: 推送到 GitCode ────────────────────────────
def git_push():
    """git add + commit + push 到远程仓库."""
    heading("1. Git Push")

    config = load_config()
    remote = config.get("git_remote", CONFIG_TEMPLATE["git_remote"])

    # 检查是否有未提交的更改
    code, output = run("git status --porcelain", cwd=ROOT)
    if code != 0:
        fail(f"git status 失败: {output}")
        return

    if not output.strip():
        # 没有更改，直接尝试 push
        print("  没有新的更改，直接 push...")
    else:
        # 有更改，需要 commit
        print(f"  发现更改:")
        for line in output.strip().split("\n"):
            print(f"    {line.strip()}")

        msg = input("\n  输入 commit 信息 (留空使用默认): ").strip()
        if not msg:
            msg = f"chore: 更新 {len(output.strip().split(chr(10)))} 个文件"

        run("git add -A", cwd=ROOT)
        code2, out2 = run(f'git commit -m "{msg}"', cwd=ROOT)
        if code2 != 0:
            fail(f"commit 失败: {out2}")
            return
        success("commit 完成")

    # Push
    code3, out3 = run(f"git push {remote} main --force", cwd=ROOT)
    if code3 == 0:
        success("push 成功")
    else:
        fail(f"push 失败: {out3}")
        print("\n  手动推送: 打开 GitCode Desktop 或终端执行:")
        print(f"    cd {ROOT}")
        print(f"    git push {remote} main --force")


# ── 操作 2: 构建 pip 包 ────────────────────────────────
def build_package(pkg_name: str) -> bool:
    """构建单个 pip 包到 dist/ 目录."""
    pkg_dir = ROOT / pkg_name
    if not pkg_dir.exists():
        fail(f"包目录不存在: {pkg_dir}")
        return False

    print(f"\n  构建 {pkg_name}...")

    # 清理旧构建
    dist_dir = pkg_dir / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    egg_dir = pkg_dir / f"{pkg_name.replace('-', '_')}.egg-info"
    if egg_dir.exists():
        shutil.rmtree(egg_dir)

    # 构建
    code, output = run(
        "python -m build --wheel --no-isolation 2>&1",
        cwd=pkg_dir
    )
    if code != 0:
        fail(f"构建失败: {output}")
        return False

    # 检查产物
    wheels = list(dist_dir.glob("*.whl"))
    if wheels:
        success(f"{pkg_name}: {wheels[0].name}")
        return True
    else:
        fail("构建完成但未找到 .whl 文件")
        return False


def build_all():
    """构建所有三个 pip 包."""
    heading("2. 构建 pip 包")
    config = load_config()
    packages = config.get("packages", CONFIG_TEMPLATE["packages"])
    ok = 0
    for pkg in packages:
        if build_package(pkg):
            ok += 1
    print(f"\n  完成: {ok}/{len(packages)} 个包构建成功")


# ── 操作 3: 发布到 PyPI ────────────────────────────────
def publish_pypi(pkg_name: str, token: str) -> bool:
    """用 twine 上传单个包到 PyPI."""
    print(f"\n  发布 {pkg_name} 到 PyPI...")

    # 检查 twine
    code, _ = run("python -m twine --version 2>&1", cwd=ROOT)
    if code != 0:
        fail("缺少 twine, 运行: pip install twine")
        return False

    dist_dir = ROOT / pkg_name / "dist"
    wheels = list(dist_dir.glob("*.whl"))
    if not wheels:
        fail(f"{pkg_name}: 没有 .whl 文件，请先构建")
        return False

    code, output = run(
        f'python -m twine upload --repository-url {PYPI_REPO} '
        f'--username __token__ --password {token} '
        f'"{str(dist_dir / "*")}" 2>&1',
        cwd=ROOT
    )
    if code == 0:
        success(f"{pkg_name} 发布成功")
        return True
    else:
        fail(f"发布失败: {output}")
        return False


def publish_all():
    """发布所有包到 PyPI."""
    heading("3. 发布到 PyPI")
    config = load_config()
    token = config.get("pypi_token", "")

    if not token:
        print("  未配置 PyPI token。")
        print("  请在 https://pypi.org/manage/account/token/ 生成一个 token")
        print("  然后填到 .fanlang.json 的 pypi_token 字段")
        return

    packages = config.get("packages", CONFIG_TEMPLATE["packages"])
    ok = 0
    for pkg in packages:
        if publish_pypi(pkg, token):
            ok += 1
    print(f"\n  完成: {ok}/{len(packages)} 个包发布成功")


# ── 操作 4: 配置向导 ────────────────────────────────────
def setup_wizard():
    """首次配置：引导用户填写必要信息."""
    heading("首次配置向导")
    config = load_config()

    print("\n  PyPI: 需要 API Token 才能发布包")
    print("  获取方式: https://pypi.org/manage/account/token/ → 创建 token → 复制")
    token = input(f"  PyPI Token [{config.get('pypi_token', '')[:8] + '...' if config.get('pypi_token') else '未配置'}]: ").strip()
    if token:
        config["pypi_token"] = token

    remote = input(f"  Git 远程地址 [{config.get('git_remote', CONFIG_TEMPLATE['git_remote'])}]: ").strip()
    if remote:
        config["git_remote"] = remote

    save_config(config)
    success("配置已保存到 .fanlang.json")


# ── 操作 5: 一键发布 ────────────────────────────────────
def publish_one_click():
    """一键执行全流程: 构建 → 测试 → push → 发布."""
    heading("一键发布")

    # 1. 推送到 GitCode
    print("\n▶ Step 1/3: 推送到 GitCode")
    git_push()

    # 2. 构建 pip 包
    print("\n▶ Step 2/3: 构建 pip 包")
    config = load_config()
    packages = config.get("packages", CONFIG_TEMPLATE["packages"])
    all_built = all(build_package(pkg) for pkg in packages)

    if not all_built:
        fail("部分包构建失败，跳过 PyPI 发布")
        return

    # 3. 发布到 PyPI
    print("\n▶ Step 3/3: 发布到 PyPI")
    token = config.get("pypi_token", "")
    if not token:
        print("  跳过 PyPI 发布 (未配置 token)")
        print("  运行 'python publish.py --setup' 配置 token")
        return

    ok = 0
    for pkg in packages:
        if publish_pypi(pkg, token):
            ok += 1

    heading(f"发布完成: GitCode✓ | PyPI {ok}/{len(packages)}")


# ── 主菜单 ──────────────────────────────────────────────
MENU = textwrap.dedent("""
  凡语 FanLang — 发布自动化

  [1] 推送到 GitCode  (git add + commit + push)
  [2] 构建 pip 包     (build wheel)
  [3] 发布到 PyPI     (twine upload)
  [4] 一键发布         (全流程)
  [5] 配置向导         (设置 token/remote)
  [6] 查看仓库状态     (git status + 包版本)

  [0] 退出
""").strip()


def show_status():
    heading("仓库状态")
    code, out = run("git log --oneline -3", cwd=ROOT)
    print("  最近提交:")
    for line in out.strip().split("\n"):
        print(f"    {line.strip()}")

    print("\n  包版本:")
    for pkg in ["fanlang", "fanlang-streamlit", "fanlang-langchain"]:
        toml = ROOT / pkg / "pyproject.toml"
        if toml.exists():
            content = toml.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if 'version' in line and '=' in line:
                    print(f"    {pkg}: {line.strip().split('=')[-1].strip().strip('\"')}")
                    break

    print(f"\n  待推送更改:")
    code2, out2 = run("git status --short", cwd=ROOT)
    if out2.strip():
        for line in out2.strip().split("\n"):
            print(f"    {line.strip()}")
    else:
        print("    (无)")


def main():
    os.chdir(str(ROOT))
    args = sys.argv[1:]

    # 快捷命令
    if "--setup" in args:
        setup_wizard()
        return
    if "--push" in args:
        git_push()
        return
    if "--build" in args:
        build_all()
        return
    if "--publish" in args:
        publish_all()
        return
    if "--all" in args:
        publish_one_click()
        return

    # 交互式菜单
    while True:
        print(MENU)
        choice = input("  选 [0-6]: ").strip()

        if choice == "1":
            git_push()
        elif choice == "2":
            build_all()
        elif choice == "3":
            publish_all()
        elif choice == "4":
            publish_one_click()
        elif choice == "5":
            setup_wizard()
        elif choice == "6":
            show_status()
        elif choice == "0":
            print("  退出")
            break
        else:
            print("  无效选项")
        print()


if __name__ == "__main__":
    main()
