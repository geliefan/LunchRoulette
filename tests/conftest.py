#!/usr/bin/env python3
"""
テスト用のパス設定スクリプト

このスクリプトをテストファイルでインポートすることで、
プロジェクトルートをPythonパスに追加し、
相対インポートを可能にします。
"""

import sys
import os
from pathlib import Path

# プロジェクトルートを取得
project_root = Path(__file__).parent.parent
src_path = project_root / "src"

# Pythonパスに追加
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))