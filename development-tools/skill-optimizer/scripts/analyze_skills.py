#!/usr/bin/env python3
"""
スキル分析ツール

スキルリポジトリを分析し、重複や類似性を検出します。
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class SkillAnalyzer:
    """スキルを分析して重複を検出するクラス"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.skills: List[Dict] = []

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
                'path': file_path,
                'name': None,
                'description': None,
                'content': content,
                'error': 'YAMLフロントマターが見つかりません'
            }

        yaml_content = yaml_match.group(1)
        markdown_content = yaml_match.group(2)

        try:
            metadata = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return {
                'path': file_path,
                'name': None,
                'description': None,
                'content': markdown_content,
                'error': f'YAML解析エラー: {e}'
            }

        return {
            'path': file_path,
            'relative_path': file_path.relative_to(self.base_path),
            'name': metadata.get('name'),
            'description': metadata.get('description'),
            'content': markdown_content,
            'word_count': len(markdown_content.split()),
            'error': None
        }

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """2つのテキストの類似度を計算（単純な単語ベースの手法）"""
        if not text1 or not text2:
            return 0.0

        # 単語に分割
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        # Jaccard類似度を計算
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def find_duplicates(self, threshold: float = 0.3) -> List[Tuple[Dict, Dict, float]]:
        """重複または類似したスキルを検出"""
        duplicates = []

        for i, skill1 in enumerate(self.skills):
            if skill1.get('error'):
                continue

            for skill2 in self.skills[i + 1:]:
                if skill2.get('error'):
                    continue

                # 説明の類似度
                desc_similarity = self.calculate_similarity(
                    skill1.get('description', ''),
                    skill2.get('description', '')
                )

                # 内容の類似度
                content_similarity = self.calculate_similarity(
                    skill1.get('content', ''),
                    skill2.get('content', '')
                )

                # 総合類似度（説明を重視）
                overall_similarity = desc_similarity * 0.6 + content_similarity * 0.4

                if overall_similarity >= threshold:
                    duplicates.append((skill1, skill2, overall_similarity))

        # 類似度の高い順にソート
        duplicates.sort(key=lambda x: x[2], reverse=True)
        return duplicates

    def find_large_skills(self, word_threshold: int = 3000) -> List[Dict]:
        """大きすぎるスキル（分割候補）を検出"""
        large_skills = []
        for skill in self.skills:
            if skill.get('error'):
                continue
            word_count = skill.get('word_count', 0)
            if word_count >= word_threshold:
                large_skills.append(skill)

        large_skills.sort(key=lambda x: x.get('word_count', 0), reverse=True)
        return large_skills

    def analyze(self):
        """スキルリポジトリ全体を分析"""
        print(f"スキルを検索中: {self.base_path}")
        skill_files = self.find_skill_files()
        print(f"見つかったスキル: {len(skill_files)}個\n")

        # スキルファイルを解析
        print("スキルを解析中...")
        for skill_file in skill_files:
            skill_data = self.parse_skill_file(skill_file)
            self.skills.append(skill_data)

        # エラーのあるスキルを報告
        error_skills = [s for s in self.skills if s.get('error')]
        if error_skills:
            print(f"\n⚠️  エラーのあるスキル: {len(error_skills)}個")
            for skill in error_skills:
                print(f"  - {skill['path']}: {skill['error']}")

        # 重複を検出
        print("\n重複を検出中...")
        duplicates = self.find_duplicates()

        # 大きなスキルを検出
        large_skills = self.find_large_skills()

        # レポートを生成
        self.generate_report(duplicates, large_skills)

    def generate_report(self, duplicates: List[Tuple], large_skills: List[Dict]):
        """分析レポートを生成"""
        print("\n" + "=" * 80)
        print("スキル分析レポート")
        print("=" * 80)

        print(f"\n総スキル数: {len(self.skills)}")

        # カテゴリ別の集計
        categories = {}
        for skill in self.skills:
            if skill.get('error'):
                continue
            parts = skill['relative_path'].parts
            if len(parts) > 1:
                category = parts[0]
                categories[category] = categories.get(category, 0) + 1

        print(f"カテゴリ数: {len(categories)}")
        print("\nカテゴリ別スキル数:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}")

        # 重複レポート
        print("\n" + "-" * 80)
        print("重複・類似スキル分析")
        print("-" * 80)

        if not duplicates:
            print("\n✓ 重複は検出されませんでした")
        else:
            print(f"\n検出された類似ペア: {len(duplicates)}組\n")

            # 類似度別に分類
            high_similarity = [d for d in duplicates if d[2] >= 0.7]
            medium_similarity = [d for d in duplicates if 0.5 <= d[2] < 0.7]
            low_similarity = [d for d in duplicates if 0.3 <= d[2] < 0.5]

            if high_similarity:
                print("### 高類似度（≥70%）- 統合を強く推奨")
                for skill1, skill2, similarity in high_similarity:
                    print(f"\n- **{skill1['name']}** と **{skill2['name']}**")
                    print(f"  - 類似度: {similarity:.1%}")
                    print(f"  - パス1: {skill1['relative_path']}")
                    print(f"  - パス2: {skill2['relative_path']}")
                    print(f"  - 説明1: {skill1['description'][:80]}...")
                    print(f"  - 説明2: {skill2['description'][:80]}...")

            if medium_similarity:
                print("\n### 中類似度（50-69%）- 統合を検討")
                for skill1, skill2, similarity in medium_similarity[:5]:  # 最大5個表示
                    print(f"\n- **{skill1['name']}** と **{skill2['name']}**")
                    print(f"  - 類似度: {similarity:.1%}")
                    print(f"  - パス1: {skill1['relative_path']}")
                    print(f"  - パス2: {skill2['relative_path']}")

            if low_similarity:
                print(f"\n### 低類似度（30-49%）: {len(low_similarity)}組")
                print("（関連性はあるがクロスリファレンスで十分な可能性）")

        # 大きなスキルレポート
        print("\n" + "-" * 80)
        print("大きなスキル分析（分割候補）")
        print("-" * 80)

        if not large_skills:
            print("\n✓ 分割が必要な大きなスキルはありません")
        else:
            print(f"\n検出された大きなスキル: {len(large_skills)}個\n")
            for skill in large_skills[:10]:  # 最大10個表示
                print(f"- **{skill['name']}**")
                print(f"  - パス: {skill['relative_path']}")
                print(f"  - 単語数: {skill['word_count']:,}")
                print(f"  - 推奨: 機能を分析して複数のスキルへの分割を検討")
                print()

        print("=" * 80)
        print("分析完了")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='スキルリポジトリを分析して重複と最適化の機会を検出'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='スキルリポジトリのパス（デフォルト: カレントディレクトリ）'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.3,
        help='重複検出の類似度閾値（0.0-1.0、デフォルト: 0.3）'
    )
    parser.add_argument(
        '--word-threshold',
        type=int,
        default=3000,
        help='大きなスキルと判断する単語数（デフォルト: 3000）'
    )

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"エラー: パスが存在しません: {args.path}", file=sys.stderr)
        sys.exit(1)

    analyzer = SkillAnalyzer(args.path)
    analyzer.analyze()


if __name__ == '__main__':
    main()
