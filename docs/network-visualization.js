/**
 * Skill Network Visualization Functions
 * Extracts keywords from skills and generates network visualization data
 */

// ネットワーク図関連の変数
let network = null;
let networkData = null;

/**
 * 日本語テキストから単語を抽出（簡易版）
 * @param {string} text - 抽出元のテキスト
 * @returns {string[]} - 抽出されたキーワードの配列
 */
function extractKeywords(text) {
    // ストップワードリスト（除外する単語）
    const stopWords = new Set([
        'の', 'は', 'を', 'に', 'が', 'で', 'と', 'する', 'から', 'まで',
        'や', 'も', 'として', 'により', 'について', 'における', 'ため',
        'こと', 'もの', 'れる', 'られる', 'させる', 'せる', 'できる',
        '等', 'など', 'さらに', 'また', 'および', 'または', 'ただし',
        'これ', 'それ', 'あれ', 'この', 'その', 'あの', 'どの',
        'ある', 'いる', 'なる', 'です', 'ます', 'だ', 'である',
        'に関する', 'に対する', 'による', 'によって', '使用', '活用'
    ]);

    // テキストを2-5文字の単語に分割（簡易的な方法）
    const words = new Set();
    const cleanText = text.replace(/[、。！？\s\-_]/g, '');

    // カタカナ・ひらがな・漢字の連続を抽出
    const patterns = [
        /[ァ-ヶー]{2,}/g,  // カタカナ
        /[ぁ-ん]{2,}/g,    // ひらがな
        /[一-龯]{2,}/g     // 漢字
    ];

    patterns.forEach(pattern => {
        const matches = text.match(pattern);
        if (matches) {
            matches.forEach(word => {
                if (word.length >= 2 && word.length <= 6 && !stopWords.has(word)) {
                    words.add(word);
                }
            });
        }
    });

    // 英数字の単語も抽出
    const engWords = text.match(/[A-Za-z]{3,}/g);
    if (engWords) {
        engWords.forEach(word => {
            const lower = word.toLowerCase();
            if (lower.length >= 3 && lower.length <= 15) {
                words.add(lower);
            }
        });
    }

    return Array.from(words);
}

/**
 * スキルから単語を抽出
 * @param {Array} skills - スキルの配列
 * @returns {Array} - キーワードを含むスキルの配列
 */
function analyzeSkills(skills) {
    return skills.map(skill => {
        const text = `${skill.name} ${skill.description} ${skill.category}`;
        const keywords = extractKeywords(text);
        return {
            ...skill,
            keywords: keywords
        };
    });
}

/**
 * ネットワークデータを生成
 * @param {Array} skills - スキルの配列
 * @param {number} minCommonWords - 最小共通単語数
 * @param {string} categoryFilter - カテゴリフィルター
 * @returns {Object} - ノードとエッジを含むネットワークデータ
 */
function generateNetworkData(skills, minCommonWords = 2, categoryFilter = 'all') {
    const analyzedSkills = analyzeSkills(skills);

    // カテゴリでフィルタリング
    const filteredSkills = categoryFilter === 'all'
        ? analyzedSkills
        : analyzedSkills.filter(s => s.category === categoryFilter);

    // ノードを作成
    const nodes = filteredSkills.map(skill => ({
        id: skill.id,
        label: skill.name,
        title: `${skill.name}\n${skill.description}`,
        group: skill.category,
        keywords: skill.keywords
    }));

    // エッジを作成（共通する単語を持つスキル同士を繋ぐ）
    const edges = [];

    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            const node1 = nodes[i];
            const node2 = nodes[j];

            // 共通する単語を見つける
            const commonWords = node1.keywords.filter(word =>
                node2.keywords.includes(word)
            );

            if (commonWords.length >= minCommonWords) {
                const edgeId = `${node1.id}-${node2.id}`;
                edges.push({
                    id: edgeId,
                    from: node1.id,
                    to: node2.id,
                    value: commonWords.length,
                    title: `共通単語: ${commonWords.join(', ')}`,
                    commonWords: commonWords
                });
            }
        }
    }

    return { nodes, edges };
}

// Export for Node.js (for testing)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        extractKeywords,
        analyzeSkills,
        generateNetworkData
    };
}
