#!/usr/bin/env python3
"""
スキルカタログを生成するスクリプト
各スキルのSKILL.mdからメタデータを抽出してJSONを生成
"""

import json
import os
import re
import yaml
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

        # PyYAMLを使用して正しくパース
        try:
            metadata = yaml.safe_load(yaml_content)
            if metadata and isinstance(metadata, dict):
                # descriptionが複数行の場合、改行と余分な空白を整形
                if 'description' in metadata and isinstance(metadata['description'], str):
                    # 複数行のdescriptionを1行にまとめ、余分な空白を削除
                    metadata['description'] = ' '.join(metadata['description'].split())
                return metadata
        except yaml.YAMLError as e:
            print(f"YAML parsing error in {file_path}: {e}")
            return None

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def get_category_name(relative_path):
    """相対パスから適切なカテゴリ名を取得"""
    # カテゴリマッピング（相対パス → 日本語カテゴリ名）
    category_mapping = {
        # データサイエンス関連
        'src/analysis/data-science/fundamentals': 'データサイエンス基礎',
        'src/analysis/data-science/modeling': 'データサイエンスモデリング',
        'src/analysis/data-science/business-application': 'データサイエンスビジネス応用',
        'src/analysis/data-science/advanced': 'データサイエンス発展',
        'src/analysis/data-science/mindset': 'データサイエンスマインドセット',
        # 基本カテゴリ
        'src/design': '設計',
        'src/supply-chain': 'サプライチェーン',
        'src/devops': 'DevOps',
        'src/development-tools': '開発ツール',
        'src/analysis': '分析',
        'src/code-quality': 'コード品質',
        'src/code-generation': 'コード生成',
        'src/thinking-skills': '思考スキル',
        'src/testing': 'テスト',
        'src/self-management': '自己管理',
        'src/time-management': '時間管理',
        'src/shared': '共通',
        'src/marketing': 'マーケティング',
        'src/retail': '小売',
        'src/ecommerce': 'EC',
        'src/security': 'セキュリティ',
        'src/community-tools': 'コミュニティツール',
        # AWS関連
        'src/cloud-platforms/aws/fundamentals': 'AWS基礎',
        'src/cloud-platforms/aws/compute': 'AWSコンピューティング',
        'src/cloud-platforms/aws/storage-database': 'AWSストレージ・データベース',
        'src/cloud-platforms/aws/networking': 'AWSネットワーキング',
        'src/cloud-platforms/aws/security-monitoring': 'AWSセキュリティ・監視',
        'src/cloud-platforms/aws/data-analytics-ml': 'AWSデータ分析・機械学習',
        'src/cloud-platforms/aws/developer-tools': 'AWS開発者ツール',
        'src/cloud-platforms/aws/architecture': 'AWSアーキテクチャ',
        'src/cloud-platforms/aws/infrastructure-automation': 'AWSインフラ自動化',
        # Databricks関連
        'src/databricks/fundamentals': 'Databricks基礎',
        'src/databricks/data-engineering': 'Databricksデータエンジニアリング',
        'src/databricks/ml-data-science': 'Databricks機械学習・データサイエンス',
        'src/databricks/architecture-devops': 'Databricksアーキテクチャ・DevOps',
        'src/databricks/governance-security': 'Databricksガバナンス・セキュリティ',
        'src/databricks/utilities': 'Databricksユーティリティ',
        'src/databricks/operations': 'Databricks運用',
        'src/databricks/file-formats': 'Databricksファイルフォーマット',
        'src/databricks/bi-analytics': 'DatabricksBI・分析',
        # 対人スキル関連
        'src/interpersonal-skills/communication': '対人スキル：コミュニケーション',
        'src/interpersonal-skills/collaboration-negotiation': '対人スキル：協働・交渉',
        'src/interpersonal-skills/emotional-empathy': '対人スキル：感情・共感',
        'src/interpersonal-skills/relationship-building': '対人スキル：関係構築',
        'src/interpersonal-skills/social-awareness': '対人スキル：社会的認識',
        'src/interpersonal-skills/growth-improvement': '対人スキル：成長・改善',
        # 製品開発関連
        'src/product-development/planning-research': '製品開発：計画・調査',
        'src/product-development/concept-design': '製品開発：コンセプト・デザイン',
        'src/product-development/development': '製品開発：開発',
        'src/product-development/testing-improvement': '製品開発：テスト・改善',
        'src/product-development/sales-deployment': '製品開発：営業・展開',
        'src/product-development/soft-skills': '製品開発：ソフトスキル',
    }

    parent_path = str(relative_path.parent)

    # マッピングに存在する場合はそれを返す
    if parent_path in category_mapping:
        return category_mapping[parent_path]

    # マッピングに存在しない場合は親ディレクトリ名をそのまま返す
    if relative_path.parent != Path('.'):
        return parent_path

    return 'root'


def scan_skills(base_dir='.'):
    """すべてのスキルディレクトリをスキャンしてメタデータを抽出"""
    skills = []
    base_path = Path(base_dir)

    # 除外するディレクトリ
    exclude_dirs = {'.git', '.github', 'docs', 'tests', 'node_modules', '__pycache__', '.vscode'}

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
                'category': get_category_name(relative_path)
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
