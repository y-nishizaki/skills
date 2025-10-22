#!/usr/bin/env python3
"""
スキルカタログを生成するスクリプト
各スキルのSKILL.mdからメタデータを抽出してJSONを生成
"""

import json
import os
import re
from pathlib import Path


def extract_yaml_frontmatter(file_path):
    """SKILL.mdからYAMLフロントマターを抽出"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # YAMLフロントマターを抽出（---で囲まれた部分）
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None

        yaml_content = match.group(1)

        # 簡易的なYAMLパーサー（name と description を抽出）
        metadata = {}
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                metadata[key] = value

        return metadata
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def scan_skills(base_dir='.'):
    """すべてのスキルディレクトリをスキャンしてメタデータを抽出"""
    skills = []
    base_path = Path(base_dir)

    # 除外するディレクトリ
    exclude_dirs = {'.git', '.github', 'docs', 'node_modules', '__pycache__', '.vscode'}

    # 再帰的にSKILL.mdファイルを検索
    for skill_file in base_path.rglob('SKILL.md'):
        # 除外ディレクトリをスキップ
        if any(excluded in skill_file.parts for excluded in exclude_dirs):
            continue

        metadata = extract_yaml_frontmatter(skill_file)
        if metadata and 'name' in metadata:
            # スキルディレクトリへの相対パス（リポジトリルートから）
            skill_dir = skill_file.parent
            relative_path = skill_dir.relative_to(base_path)

            skill_data = {
                'id': skill_dir.name,
                'name': metadata.get('name', skill_dir.name),
                'description': metadata.get('description', '説明がありません'),
                'path': str(relative_path),
                'category': str(relative_path.parent) if relative_path.parent != Path('.') else 'root'
            }
            skills.append(skill_data)

    # 名前でソート
    skills.sort(key=lambda x: x['name'])
    return skills


def main():
    """メイン処理"""
    # スキルリポジトリのルートディレクトリ（このスクリプトの親の親）
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    print(f"スキルをスキャン中: {repo_root}")
    skills = scan_skills(repo_root)

    print(f"見つかったスキル: {len(skills)}個")

    # JSONファイルとして保存
    output_file = script_dir / 'skills.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(skills, f, ensure_ascii=False, indent=2)

    print(f"カタログを生成しました: {output_file}")

    # スキル一覧を表示
    for skill in skills:
        print(f"  - {skill['name']} ({skill['id']})")


if __name__ == '__main__':
    main()
