#!/usr/bin/env python3
"""
スキル品質チェックツール

スキルの構造、ドキュメント、命名規則を検証します。
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List
import yaml


class QualityChecker:
    """スキルの品質をチェックするクラス"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.errors = []
        self.warnings = []
        self.recommendations = []

    def find_skill_files(self) -> List[Path]:
        """すべてのSKILL.mdファイルを検索"""
        skill_files = []
        for skill_file in self.base_path.rglob("SKILL.md"):
            skill_files.append(skill_file)
        return sorted(skill_files)

    def check_yaml_frontmatter(self, file_path: Path, content: str) -> Dict:
        """YAMLフロントマターを検証"""
        issues = {
            'errors': [],
            'warnings': [],
            'metadata': None
        }

        # YAMLフロントマターの存在確認
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

        if not yaml_match:
            issues['errors'].append('YAMLフロントマターが見つかりません')
            return issues

        yaml_content = yaml_match.group(1)

        # YAML解析
        try:
            metadata = yaml.safe_load(yaml_content)
            issues['metadata'] = metadata
        except yaml.YAMLError as e:
            issues['errors'].append(f'YAML解析エラー: {e}')
            return issues

        # 必須フィールドのチェック
        if not metadata:
            issues['errors'].append('YAMLフロントマターが空です')
            return issues

        if 'name' not in metadata:
            issues['errors'].append('必須フィールド "name" が欠落しています')
        elif not metadata['name']:
            issues['errors'].append('フィールド "name" が空です')

        if 'description' not in metadata:
            issues['errors'].append('必須フィールド "description" が欠落しています')
        elif not metadata['description']:
            issues['errors'].append('フィールド "description" が空です')
        else:
            # 説明の長さチェック
            desc_length = len(metadata['description'])
            if desc_length < 30:
                issues['warnings'].append(f'説明が短すぎます（{desc_length}文字、推奨: 30文字以上）')
            elif desc_length > 300:
                issues['warnings'].append(f'説明が長すぎます（{desc_length}文字、推奨: 300文字以下）')

        return issues

    def check_directory_structure(self, file_path: Path) -> List[str]:
        """ディレクトリ構造を検証"""
        issues = []
        skill_dir = file_path.parent

        # スキル名とディレクトリ名の確認
        dir_name = skill_dir.name

        # ケバブケースのチェック
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', dir_name):
            issues.append(f'ディレクトリ名がケバブケースではありません: {dir_name}')

        # 不要なファイル・ディレクトリの確認
        allowed_items = {'SKILL.md', 'scripts', 'references', 'assets', 'examples.md', 'reference.md'}
        for item in skill_dir.iterdir():
            if item.name not in allowed_items and not item.name.startswith('.'):
                issues.append(f'標準外のファイル/ディレクトリ: {item.name}')

        return issues

    def check_content_quality(self, content: str, metadata: Dict) -> List[str]:
        """コンテンツの品質をチェック"""
        issues = []

        # Markdown本文の抽出
        yaml_match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)', content, re.DOTALL)
        if not yaml_match:
            return issues

        markdown_content = yaml_match.group(1)

        # 単語数のチェック
        word_count = len(markdown_content.split())

        if word_count < 100:
            issues.append(f'本文が短すぎます（{word_count}語、推奨: 100語以上）')
        elif word_count > 5000:
            issues.append(f'本文が長すぎます（{word_count}語、推奨: 5000語以下、分割を検討）')

        # セクション構造のチェック
        headers = re.findall(r'^#+\s+(.+)$', markdown_content, re.MULTILINE)
        if not headers:
            issues.append('セクションヘッダーが見つかりません')

        # コードブロックの存在チェック（開発ツール系スキルの場合）
        code_blocks = re.findall(r'```', markdown_content)
        if len(code_blocks) % 2 != 0:
            issues.append('コードブロックが正しく閉じられていません')

        return issues

    def check_resource_references(self, file_path: Path, content: str) -> List[str]:
        """リソース参照の整合性をチェック"""
        issues = []
        skill_dir = file_path.parent

        # コンテンツ内のファイル参照を検索
        file_refs = re.findall(r'(?:scripts|references|assets)/[a-zA-Z0-9_/-]+\.[a-z]+', content)

        for ref in file_refs:
            ref_path = skill_dir / ref
            if not ref_path.exists():
                issues.append(f'参照されているファイルが存在しません: {ref}')

        # scriptsディレクトリのチェック
        scripts_dir = skill_dir / 'scripts'
        if scripts_dir.exists() and scripts_dir.is_dir():
            scripts = list(scripts_dir.glob('*'))
            if scripts:
                # スクリプトが実行可能かチェック
                for script in scripts:
                    if script.is_file() and script.suffix == '.py':
                        # Pythonスクリプトのシバン行チェック
                        with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                            first_line = f.readline()
                            if not first_line.startswith('#!'):
                                issues.append(f'Pythonスクリプトにシバン行がありません: {script.name}')

        return issues

    def check_skill(self, file_path: Path) -> Dict:
        """個別のスキルを総合的にチェック"""
        result = {
            'path': file_path,
            'relative_path': file_path.relative_to(self.base_path),
            'errors': [],
            'warnings': [],
            'recommendations': []
        }

        # ファイル読み込み
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            result['errors'].append(f'ファイル読み込みエラー: {e}')
            return result

        # YAMLフロントマターのチェック
        yaml_issues = self.check_yaml_frontmatter(file_path, content)
        result['errors'].extend(yaml_issues['errors'])
        result['warnings'].extend(yaml_issues['warnings'])

        metadata = yaml_issues.get('metadata')

        # ディレクトリ構造のチェック
        dir_issues = self.check_directory_structure(file_path)
        result['warnings'].extend(dir_issues)

        # コンテンツ品質のチェック
        if metadata:
            content_issues = self.check_content_quality(content, metadata)
            result['recommendations'].extend(content_issues)

            # リソース参照のチェック
            ref_issues = self.check_resource_references(file_path, content)
            result['errors'].extend(ref_issues)

        return result

    def check_all(self):
        """すべてのスキルをチェック"""
        print(f"スキルを検索中: {self.base_path}")
        skill_files = self.find_skill_files()
        print(f"見つかったスキル: {len(skill_files)}個\n")

        print("スキルを検証中...")
        results = []
        for skill_file in skill_files:
            result = self.check_skill(skill_file)
            results.append(result)

            # 問題があればリストに追加
            if result['errors']:
                self.errors.append(result)
            if result['warnings']:
                self.warnings.append(result)
            if result['recommendations']:
                self.recommendations.append(result)

        # レポート生成
        self.generate_report(results)

    def generate_report(self, results: List[Dict]):
        """品質チェックレポートを生成"""
        print("\n" + "=" * 80)
        print("スキル品質チェックレポート")
        print("=" * 80)

        total_skills = len(results)
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        recommendation_count = len(self.recommendations)

        print(f"\n総スキル数: {total_skills}")
        print(f"エラーのあるスキル: {error_count}")
        print(f"警告のあるスキル: {warning_count}")
        print(f"推奨事項のあるスキル: {recommendation_count}")

        # エラー詳細
        if self.errors:
            print("\n" + "-" * 80)
            print("❌ エラー（要修正）")
            print("-" * 80)
            for result in self.errors:
                print(f"\n**{result['relative_path']}**")
                for error in result['errors']:
                    print(f"  - {error}")

        # 警告詳細
        if self.warnings:
            print("\n" + "-" * 80)
            print("⚠️  警告（改善推奨）")
            print("-" * 80)
            for result in self.warnings[:10]:  # 最大10個表示
                print(f"\n**{result['relative_path']}**")
                for warning in result['warnings']:
                    print(f"  - {warning}")

            if len(self.warnings) > 10:
                print(f"\n... 他 {len(self.warnings) - 10} 件の警告")

        # 推奨事項
        if self.recommendations:
            print("\n" + "-" * 80)
            print("💡 推奨事項（オプション）")
            print("-" * 80)
            for result in self.recommendations[:10]:  # 最大10個表示
                print(f"\n**{result['relative_path']}**")
                for rec in result['recommendations']:
                    print(f"  - {rec}")

            if len(self.recommendations) > 10:
                print(f"\n... 他 {len(self.recommendations) - 10} 件の推奨事項")

        # サマリー
        print("\n" + "=" * 80)
        if error_count == 0 and warning_count == 0:
            print("✅ すべてのスキルが品質基準を満たしています！")
        elif error_count == 0:
            print("✓ 重大なエラーはありません（警告はあります）")
        else:
            print(f"⚠️  {error_count} 個のスキルに修正が必要なエラーがあります")
        print("=" * 80)

        # 終了コード
        return 1 if error_count > 0 else 0


def main():
    parser = argparse.ArgumentParser(
        description='スキルの品質をチェック'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='スキルリポジトリのパス（デフォルト: カレントディレクトリ）'
    )

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"エラー: パスが存在しません: {args.path}", file=sys.stderr)
        sys.exit(1)

    checker = QualityChecker(args.path)
    exit_code = checker.check_all()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
