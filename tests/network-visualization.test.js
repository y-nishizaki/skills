/**
 * Tests for skill network visualization functions
 */

const { extractKeywords, analyzeSkills, generateNetworkData } = require('../docs/network-visualization.js');

describe('Network Visualization', () => {
  describe('extractKeywords', () => {
    test('should extract Japanese keywords from text', () => {
      const text = 'API設計とGraphQL設計';
      const keywords = extractKeywords(text);

      expect(keywords).toBeDefined();
      expect(Array.isArray(keywords)).toBe(true);
      expect(keywords.length).toBeGreaterThan(0);
    });

    test('should extract English keywords from text', () => {
      const text = 'REST API design and GraphQL implementation';
      const keywords = extractKeywords(text);

      expect(keywords).toBeDefined();
      expect(Array.isArray(keywords)).toBe(true);
      expect(keywords).toContain('rest');
      expect(keywords).toContain('api');
      expect(keywords).toContain('design');
      expect(keywords).toContain('graphql');
      expect(keywords).toContain('implementation');
    });

    test('should filter out stop words', () => {
      const text = 'これはテストです';
      const keywords = extractKeywords(text);

      expect(keywords).not.toContain('これ');
      expect(keywords).not.toContain('です');
    });

    test('should handle empty text', () => {
      const keywords = extractKeywords('');

      expect(keywords).toBeDefined();
      expect(Array.isArray(keywords)).toBe(true);
      expect(keywords.length).toBe(0);
    });

    test('should extract keywords of appropriate length', () => {
      const text = 'API設計とデータベース最適化';
      const keywords = extractKeywords(text);

      keywords.forEach(keyword => {
        if (/[A-Za-z]/.test(keyword)) {
          // English words: 3-15 characters
          expect(keyword.length).toBeGreaterThanOrEqual(3);
          expect(keyword.length).toBeLessThanOrEqual(15);
        } else {
          // Japanese words: 2-6 characters
          expect(keyword.length).toBeGreaterThanOrEqual(2);
          expect(keyword.length).toBeLessThanOrEqual(6);
        }
      });
    });

    test('should extract katakana keywords', () => {
      const text = 'データベース管理とAPI設計';
      const keywords = extractKeywords(text);

      expect(keywords).toContain('データベース');
    });

    test('should extract hiragana keywords', () => {
      const text = 'これはテストです';
      const keywords = extractKeywords(text);

      expect(keywords).toContain('テスト');
    });

    test('should handle mixed Japanese and English text', () => {
      const text = 'RESTful APIの設計とGraphQLの実装';
      const keywords = extractKeywords(text);

      expect(keywords.some(k => /[A-Za-z]/.test(k))).toBe(true); // Has English
      expect(keywords.some(k => /[ぁ-ん]/.test(k) || /[ァ-ヶー]/.test(k) || /[一-龯]/.test(k))).toBe(true); // Has Japanese
    });
  });

  describe('analyzeSkills', () => {
    test('should analyze skills and extract keywords', () => {
      const skills = [
        {
          id: 'test-skill',
          name: 'API設計',
          description: 'RESTful API設計とGraphQL設計',
          category: '設計'
        }
      ];

      const analyzed = analyzeSkills(skills);

      expect(analyzed).toBeDefined();
      expect(Array.isArray(analyzed)).toBe(true);
      expect(analyzed.length).toBe(1);
      expect(analyzed[0]).toHaveProperty('keywords');
      expect(Array.isArray(analyzed[0].keywords)).toBe(true);
      expect(analyzed[0].keywords.length).toBeGreaterThan(0);
    });

    test('should preserve original skill properties', () => {
      const skills = [
        {
          id: 'test-skill',
          name: 'テストスキル',
          description: 'テスト用のスキル',
          category: 'テスト',
          path: 'test/test-skill'
        }
      ];

      const analyzed = analyzeSkills(skills);

      expect(analyzed[0].id).toBe('test-skill');
      expect(analyzed[0].name).toBe('テストスキル');
      expect(analyzed[0].description).toBe('テスト用のスキル');
      expect(analyzed[0].category).toBe('テスト');
      expect(analyzed[0].path).toBe('test/test-skill');
    });

    test('should handle empty skills array', () => {
      const analyzed = analyzeSkills([]);

      expect(analyzed).toEqual([]);
    });

    test('should extract keywords from all skill fields', () => {
      const skills = [
        {
          id: 'test-skill',
          name: 'API',
          description: 'GraphQL',
          category: '設計'
        }
      ];

      const analyzed = analyzeSkills(skills);

      // Keywords should include words from name, description, and category
      const allKeywords = analyzed[0].keywords.join(' ');
      expect(allKeywords).toContain('api');
      expect(allKeywords).toContain('graphql');
      expect(allKeywords).toContain('設計');
    });
  });

  describe('generateNetworkData', () => {
    const testSkills = [
      {
        id: 'skill-1',
        name: 'API設計',
        description: 'RESTful API設計とGraphQL',
        category: '設計'
      },
      {
        id: 'skill-2',
        name: 'API実装',
        description: 'RESTful API実装',
        category: '開発'
      },
      {
        id: 'skill-3',
        name: 'データベース設計',
        description: 'データベース設計と最適化',
        category: '設計'
      }
    ];

    test('should generate nodes and edges', () => {
      const networkData = generateNetworkData(testSkills, 2, 'all');

      expect(networkData).toBeDefined();
      expect(networkData).toHaveProperty('nodes');
      expect(networkData).toHaveProperty('edges');
      expect(Array.isArray(networkData.nodes)).toBe(true);
      expect(Array.isArray(networkData.edges)).toBe(true);
    });

    test('should create nodes with required properties', () => {
      const networkData = generateNetworkData(testSkills, 2, 'all');

      expect(networkData.nodes.length).toBe(3);

      networkData.nodes.forEach(node => {
        expect(node).toHaveProperty('id');
        expect(node).toHaveProperty('label');
        expect(node).toHaveProperty('title');
        expect(node).toHaveProperty('group');
        expect(node).toHaveProperty('keywords');

        expect(typeof node.id).toBe('string');
        expect(typeof node.label).toBe('string');
        expect(typeof node.title).toBe('string');
        expect(typeof node.group).toBe('string');
        expect(Array.isArray(node.keywords)).toBe(true);
      });
    });

    test('should create edges only for skills with sufficient common keywords', () => {
      const networkData = generateNetworkData(testSkills, 2, 'all');

      networkData.edges.forEach(edge => {
        expect(edge).toHaveProperty('id');
        expect(edge).toHaveProperty('from');
        expect(edge).toHaveProperty('to');
        expect(edge).toHaveProperty('value');
        expect(edge).toHaveProperty('title');
        expect(edge).toHaveProperty('commonWords');

        expect(typeof edge.id).toBe('string');
        expect(typeof edge.from).toBe('string');
        expect(typeof edge.to).toBe('string');
        expect(typeof edge.value).toBe('number');
        expect(Array.isArray(edge.commonWords)).toBe(true);
        expect(edge.commonWords.length).toBeGreaterThanOrEqual(2);
      });
    });

    test('should filter by category', () => {
      const networkData = generateNetworkData(testSkills, 1, '設計');

      expect(networkData.nodes.length).toBe(2); // Only skill-1 and skill-3
      networkData.nodes.forEach(node => {
        expect(node.group).toBe('設計');
      });
    });

    test('should respect minimum common words threshold', () => {
      const networkData = generateNetworkData(testSkills, 3, 'all');

      networkData.edges.forEach(edge => {
        expect(edge.commonWords.length).toBeGreaterThanOrEqual(3);
        expect(edge.value).toBeGreaterThanOrEqual(3);
      });
    });

    test('should return all nodes when category is "all"', () => {
      const networkData = generateNetworkData(testSkills, 1, 'all');

      expect(networkData.nodes.length).toBe(3);
    });

    test('should create edge IDs in correct format', () => {
      const networkData = generateNetworkData(testSkills, 1, 'all');

      networkData.edges.forEach(edge => {
        expect(edge.id).toMatch(/^.+-.+$/);
        expect(edge.id).toBe(`${edge.from}-${edge.to}`);
      });
    });

    test('should not create duplicate edges', () => {
      const networkData = generateNetworkData(testSkills, 1, 'all');

      const edgeIds = networkData.edges.map(e => e.id);
      const uniqueEdgeIds = new Set(edgeIds);

      expect(edgeIds.length).toBe(uniqueEdgeIds.size);
    });

    test('should include common words in edge title', () => {
      const networkData = generateNetworkData(testSkills, 1, 'all');

      networkData.edges.forEach(edge => {
        expect(edge.title).toContain('共通単語:');
        edge.commonWords.forEach(word => {
          expect(edge.title).toContain(word);
        });
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle missing skills data gracefully', () => {
      const networkData = generateNetworkData([], 2, 'all');

      expect(networkData.nodes).toEqual([]);
      expect(networkData.edges).toEqual([]);
    });

    test('should handle invalid category filter', () => {
      const skills = [
        {
          id: 'skill-1',
          name: 'テスト',
          description: 'テスト',
          category: '設計'
        }
      ];

      const networkData = generateNetworkData(skills, 2, '存在しないカテゴリ');

      expect(networkData.nodes).toEqual([]);
      expect(networkData.edges).toEqual([]);
    });

    test('should handle skills with no common keywords', () => {
      const skills = [
        {
          id: 'skill-1',
          name: 'AAAA',
          description: 'BBBB',
          category: 'cat1'
        },
        {
          id: 'skill-2',
          name: 'CCCC',
          description: 'DDDD',
          category: 'cat2'
        }
      ];

      const networkData = generateNetworkData(skills, 2, 'all');

      expect(networkData.nodes.length).toBe(2);
      expect(networkData.edges.length).toBe(0);
    });

    test('should handle high minimum common words threshold', () => {
      const skills = [
        {
          id: 'skill-1',
          name: 'API',
          description: 'API design',
          category: '設計'
        },
        {
          id: 'skill-2',
          name: 'API',
          description: 'API implementation',
          category: '開発'
        }
      ];

      const networkData = generateNetworkData(skills, 100, 'all');

      expect(networkData.nodes.length).toBe(2);
      expect(networkData.edges.length).toBe(0);
    });
  });

  describe('Integration Tests', () => {
    test('should handle real skills data structure', () => {
      const realSkills = require('../docs/skills.json');

      const networkData = generateNetworkData(realSkills, 2, 'all');

      expect(networkData).toBeDefined();
      expect(networkData.nodes.length).toBe(realSkills.length);
      expect(networkData.edges.length).toBeGreaterThanOrEqual(0);
    });

    test('should create reasonable number of connections with real data', () => {
      const realSkills = require('../docs/skills.json');

      const networkData = generateNetworkData(realSkills, 2, 'all');

      // With real data, there should be some connections
      expect(networkData.edges.length).toBeGreaterThan(0);

      // But not too many (not every node connected to every other)
      const maxPossibleEdges = (networkData.nodes.length * (networkData.nodes.length - 1)) / 2;
      expect(networkData.edges.length).toBeLessThan(maxPossibleEdges);
    });

    test('should work with different minCommonWords thresholds', () => {
      const realSkills = require('../docs/skills.json');

      const data1 = generateNetworkData(realSkills, 1, 'all');
      const data2 = generateNetworkData(realSkills, 3, 'all');
      const data3 = generateNetworkData(realSkills, 5, 'all');

      // Higher threshold should result in fewer edges
      expect(data1.edges.length).toBeGreaterThanOrEqual(data2.edges.length);
      expect(data2.edges.length).toBeGreaterThanOrEqual(data3.edges.length);
    });

    test('should work with category filters on real data', () => {
      const realSkills = require('../docs/skills.json');

      // Get unique categories
      const categories = [...new Set(realSkills.map(s => s.category))];

      if (categories.length > 0) {
        const category = categories[0];
        const networkData = generateNetworkData(realSkills, 2, category);

        const expectedCount = realSkills.filter(s => s.category === category).length;
        expect(networkData.nodes.length).toBe(expectedCount);

        networkData.nodes.forEach(node => {
          expect(node.group).toBe(category);
        });
      }
    });
  });
});
