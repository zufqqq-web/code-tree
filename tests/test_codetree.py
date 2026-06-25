import unittest
import os
import tempfile
import shutil

from codetree.scanner import count_lines, count_functions_and_classes, GitignoreRules, GitignoreScanner
from codetree.languages import calculate_language_stats
from codetree.frameworks import detect_frameworks
from codetree.prioritization import get_file_role, calculate_importance_scores, build_import_graph

class TestCodeTreeScanner(unittest.TestCase):
    def test_count_lines(self):
        content = "line 1\n\n  line 2  \n\nline 3\n"
        self.assertEqual(count_lines(content), 3)
        
    def test_count_functions_and_classes_python(self):
        code = "class A:\n  def method(self):\n    pass\n\ndef func():\n  pass"
        self.assertEqual(count_functions_and_classes("test.py", code), 3) # Class A, method, func

    def test_gitignore_matching(self):
        # We test gitignore rules matching logic
        rules = GitignoreRules("/workspace", ["node_modules/", "*.log", "/*.json", "!important.log"])
        self.assertTrue(rules.matches("/workspace/node_modules/dep/file.js", is_dir=True))
        self.assertTrue(rules.matches("/workspace/error.log"))
        self.assertFalse(rules.matches("/workspace/important.log"))
        # Relative to root check: "/*.json" matches root.json but not subdir/root.json
        self.assertTrue(rules.matches("/workspace/config.json"))
        self.assertFalse(rules.matches("/workspace/subdir/config.json"))

class TestCodeTreeLanguages(unittest.TestCase):
    def test_calculate_language_stats(self):
        files = [
            {'ext': '.py', 'lines': 100},
            {'ext': '.py', 'lines': 100},
            {'ext': '.ts', 'lines': 300},
            {'ext': '.json', 'lines': 500},
        ]
        # Total line count = 1000. Py = 20%, TS = 30%, JSON = 50%
        stats = calculate_language_stats(files)
        self.assertEqual(stats['TypeScript'], 30.0)
        self.assertEqual(stats['Python'], 20.0)
        self.assertEqual(stats['JSON'], 50.0)

        # Test excluding configs
        stats_no_config = calculate_language_stats(files, exclude_configs=True)
        # Total line count = 500 (Py=200, TS=300). Py = 40%, TS = 60%
        self.assertEqual(stats_no_config['TypeScript'], 60.0)
        self.assertEqual(stats_no_config['Python'], 40.0)
        self.assertNotIn('JSON', stats_no_config)

class TestCodeTreeFrameworks(unittest.TestCase):
    def test_detect_frameworks(self):
        files = [
            {
                'rel_path': 'package.json',
                'content': '{"dependencies": {"react": "^18.0.0", "next": "^13.0.0"}}',
                'ext': '.json'
            },
            {
                'rel_path': 'requirements.txt',
                'content': 'fastapi>=0.95.0\nuvicorn\ndjango==4.2',
                'ext': '.txt'
            },
            {
                'rel_path': 'tailwind.config.js',
                'content': 'module.exports = {}',
                'ext': '.js'
            }
        ]
        frameworks = detect_frameworks(files)
        self.assertIn('React', frameworks)
        self.assertIn('Next.js', frameworks)
        self.assertIn('FastAPI', frameworks)
        self.assertIn('Django', frameworks)
        self.assertIn('Tailwind CSS', frameworks)

class TestCodeTreePrioritization(unittest.TestCase):
    def test_get_file_role(self):
        # Existing tests
        self.assertEqual(get_file_role("src/utils/math.ts"), "helper")
        self.assertEqual(get_file_role("src/userDb.ts"), "data_layer")
        self.assertEqual(get_file_role("src/app_router.js"), "routing")
        self.assertEqual(get_file_role("src/components/Button.tsx"), None)
        
        # New positive tests (cli, scanner, package root default)
        self.assertEqual(get_file_role("cli.py"), "entry_point")
        self.assertEqual(get_file_role("codetree/cli.py"), "entry_point")
        self.assertEqual(get_file_role("scanner.py"), "core_logic")
        self.assertEqual(get_file_role("codetree/scanner.py"), "core_logic")
        self.assertEqual(get_file_role("codetree/frameworks.py"), "core_logic")
        self.assertEqual(get_file_role("codetree/prioritization.py"), "core_logic")
        self.assertEqual(get_file_role("codetree/llm_client.py"), "core_logic")
        self.assertEqual(get_file_role("codetree/submodule/foo.py"), None) # exceeds package root depth
        self.assertEqual(get_file_role("tests/test_codetree.py"), "test")
        
        # Negative tests for protective rules
        self.assertNotEqual(get_file_role("client.py"), "entry_point")
        self.assertNotEqual(get_file_role("scorer.py"), "core_logic")
        self.assertNotEqual(get_file_role("scores.py"), "core_logic")
        self.assertNotEqual(get_file_role("domain.py"), "entry_point")
        self.assertNotEqual(get_file_role("mapper.py"), "entry_point")
        self.assertNotEqual(get_file_role("application_logger.py"), "entry_point")
        
        # Additional checks that they are None (except client.py/scorer.py/etc. if in package root,
        # but here they are depth 1. Since depth 1 is considered in package root by fallback, let's verify if they get core_logic)
        # client.py has depth 1, so it gets core_logic by default python rule, but not entry_point.

        
    def test_import_graph_and_scores(self):
        files = [
            {
                'rel_path': 'main.py',
                'content': 'import core.db\nfrom utils.helper import format',
                'ext': '.py',
                'lines': 10,
                'declarations': 1
            },
            {
                'rel_path': 'core/db.py',
                'content': 'class Database:\n  pass',
                'ext': '.py',
                'lines': 20,
                'declarations': 1
            },
            {
                'rel_path': 'utils/helper.py',
                'content': 'def format(s):\n  return s',
                'ext': '.py',
                'lines': 15,
                'declarations': 1
            }
        ]
        
        graph = build_import_graph(files)
        # core/db.py should be referenced once, utils/helper.py referenced once, main.py referenced 0 times.
        self.assertEqual(graph.get('core/db.py', 0), 1)
        self.assertEqual(graph.get('utils/helper.py', 0), 1)
        self.assertEqual(graph.get('main.py', 0), 0)
        
        scores = calculate_importance_scores(files, graph)
        # main.py is entry point (role = entry_point) -> +10 score.
        # core/db.py is data_layer (role = data_layer) -> no entry_point boost, but referenced once.
        self.assertGreater(scores['main.py'], 0)
        self.assertGreater(scores['core/db.py'], 0)

if __name__ == '__main__':
    unittest.main()
