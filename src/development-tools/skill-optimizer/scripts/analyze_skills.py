#!/usr/bin/env python3
"""
スキルデータ収集ツール

スキルリポジトリからメタデータと内容を収集し、JSON形式で出力します。
類似度の判断はClaudeエージェントが実行します。
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List
import yaml


class SkillCollector:
    """スキル情報を収集するクラス"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.skills: List[Dict] = []

    def _is_text_file(self, file_path: Path) -> bool:
        """ファイルがテキストファイルかどうか判定"""
        text_extensions = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.sh', '.bash', '.js', '.ts', '.html', '.css', '.xml'}
        return file_path.suffix.lower() in text_extensions

    def _read_text_file(self, file_path: Path, max_chars: int = 1000) -> str:
        """テキストファイルを読み込み（プレビュー）"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_chars)
                if len(content) == max_chars:
                    content += '...[truncated]'
                return content
        except Exception as e:
            return f'[読み込みエラー: {e}]'

    def _collect_resource_files(self, resource_dir: Path) -> List[Dict]:
        """リソースディレクトリ内のファイルを収集（中身も含む）"""
        resources = []
        for file_path in resource_dir.iterdir():
            if not file_path.is_file():
                continue

            file_info = {
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'type': 'text' if self._is_text_file(file_path) else 'binary'
            }

            # テキストファイルの場合は中身を読む
            if file_info['type'] == 'text':
                file_info['content'] = self._read_text_file(file_path, max_chars=1000)
            else:
                file_info['content'] = None

            resources.append(file_info)

        return resources

    def find_skill_files(self) -> List[Path]:
        """すべてのSKILL.mdファイルを検索"""
        skill_files = []
        for skill_file in self.base_path.rglob("SKILL.md"):
            skill_files.append(skill_file)
        return sorted(skill_files)

    def parse_skill_file(self, file_path: Path) -> Dict:
        """SKILL.mdファイルを解析してメタデータと内容を抽出"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # YAMLフロントマターを抽出
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)

        if not yaml_match:
            return {
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(self.base_path)),
                'name': None,
                'description': None,
                'content_preview': content[:200],
                'word_count': len(content.split()),
                'error': 'YAMLフロントマターが見つかりません'
            }

        yaml_content = yaml_match.group(1)
        markdown_content = yaml_match.group(2)

        try:
            metadata = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return {
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(self.base_path)),
                'name': None,
                'description': None,
                'content_preview': markdown_content[:200],
                'word_count': len(markdown_content.split()),
                'error': f'YAML解析エラー: {e}'
            }

        # カテゴリを抽出
        parts = file_path.relative_to(self.base_path).parts
        category = parts[0] if len(parts) > 1 else 'uncategorized'

        # 本文のプレビュー（最初の500文字）
        content_preview = markdown_content[:500].strip()

        # セクションヘッダーを抽出
        headers = re.findall(r'^#+\s+(.+)$', markdown_content, re.MULTILINE)

        # バンドルリソースの確認（中身も収集）
        skill_dir = file_path.parent
        resources = {
            'scripts': [],
            'references': [],
            'assets': [],
            'templates': [],
            'examples': []
        }

        for resource_type in resources.keys():
            resource_dir = skill_dir / resource_type
            if resource_dir.exists() and resource_dir.is_dir():
                resources[resource_type] = self._collect_resource_files(resource_dir)

        # examples.md や reference.md の収集
        examples_md_content = None
        reference_md_content = None

        examples_md_path = skill_dir / 'examples.md'
        if examples_md_path.exists():
            examples_md_content = self._read_text_file(examples_md_path, max_chars=1000)

        reference_md_path = skill_dir / 'reference.md'
        if reference_md_path.exists():
            reference_md_content = self._read_text_file(reference_md_path, max_chars=1000)

        return {
            'path': str(file_path),
            'relative_path': str(file_path.relative_to(self.base_path)),
            'category': category,
            'name': metadata.get('name'),
            'description': metadata.get('description'),
            'content_preview': content_preview,
            'headers': headers[:10],  # 最大10個のヘッダー
            'word_count': len(markdown_content.split()),
            'resources': resources,
            'examples_md': examples_md_content,
            'reference_md': reference_md_content,
            'error': None
        }

    def collect(self) -> Dict:
        """スキルリポジトリ全体からデータを収集"""
        print(f"スキルを検索中: {self.base_path}", file=sys.stderr)
        skill_files = self.find_skill_files()
        print(f"見つかったスキル: {len(skill_files)}個", file=sys.stderr)

        # スキルファイルを解析
        print("スキルを収集中...", file=sys.stderr)
        for skill_file in skill_files:
            skill_data = self.parse_skill_file(skill_file)
            self.skills.append(skill_data)

        # カテゴリ別の集計
        categories = {}
        for skill in self.skills:
            if skill.get('error'):
                continue
            category = skill.get('category', 'uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(skill['name'])

        # 統計情報
        stats = {
            'total_skills': len(self.skills),
            'total_categories': len(categories),
            'skills_with_errors': len([s for s in self.skills if s.get('error')]),
            'average_word_count': sum(s.get('word_count', 0) for s in self.skills if not s.get('error')) // max(len([s for s in self.skills if not s.get('error')]), 1),
            'categories': {cat: len(skills) for cat, skills in categories.items()}
        }

        return {
            'base_path': str(self.base_path),
            'stats': stats,
            'skills': self.skills
        }


def main():
    parser = argparse.ArgumentParser(
        description='スキルリポジトリからデータを収集（JSON出力）'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='スキルリポジトリのパス（デフォルト: カレントディレクトリ）'
    )
    parser.add_argument(
        '--output', '-o',
        help='出力JSONファイル（指定しない場合は標準出力）'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='整形されたJSONを出力'
    )
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='統計情報のみを出力（スキルの詳細は含めない）'
    )

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"エラー: パスが存在しません: {args.path}", file=sys.stderr)
        sys.exit(1)

    collector = SkillCollector(args.path)
    data = collector.collect()

    # サマリーのみのオプション
    if args.summary_only:
        data = {'base_path': data['base_path'], 'stats': data['stats']}

    # JSON出力
    indent = 2 if args.pretty else None
    json_output = json.dumps(data, ensure_ascii=False, indent=indent)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"\n出力完了: {args.output}", file=sys.stderr)
    else:
        print(json_output)

    print(f"\n収集完了: {data['stats']['total_skills']} スキル", file=sys.stderr)


if __name__ == '__main__':
    main()
