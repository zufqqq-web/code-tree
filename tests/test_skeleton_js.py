import unittest
from codetree.skeleton import extract_js_skeleton

class TestJSSkeleton(unittest.TestCase):
    def test_case_1_normal_function(self):
        code = "function add(a, b) {\n    return a + b;\n}"
        expected = "function add(a, b) { ... }"
        result = extract_js_skeleton(code).strip()
        self.assertIn("function add(a, b) { ... }", result)

    def test_case_2_arrow_function_no_block(self):
        code = "const double = x => x * 2;"
        result = extract_js_skeleton(code).strip()
        self.assertIn("const double = x => x * 2;", result)

    def test_case_3_template_string_with_braces(self):
        code = "function greet(name) {\n    return `Hello ${name}, you have ${count} items`;\n}"
        result = extract_js_skeleton(code).strip()
        self.assertIn("function greet(name) { ... }", result)

    def test_case_4_generic_ts(self):
        code = "function parse<T>(data: Map<string, Array<{id: number}>>): T {\n    return data.get('key');\n}"
        result = extract_js_skeleton(code).strip()
        self.assertIn("function parse<T>(data: Map<string, Array<{id: number}>>): T { ... }", result)

    def test_case_5_class_with_methods(self):
        code = "class User {\n    constructor(name) {\n        this.name = name;\n    }\n    getName() {\n        return this.name;\n    }\n}"
        result = extract_js_skeleton(code).strip()
        # We expect the class signature and method signatures, but bodies stripped
        self.assertIn("class User", result)
        self.assertIn("constructor(name) { ... }", result)
        self.assertIn("getName() { ... }", result)
        self.assertNotIn("this.name = name", result)
        self.assertNotIn("return this.name", result)

    def test_case_6_comment_with_brace(self):
        code = "// note: this uses a { trick } for parsing\nfunction foo() {\n    return 42;\n}"
        result = extract_js_skeleton(code).strip()
        self.assertIn("function foo() { ... }", result)
        # Verify comment doesn't break parsing or brace balancing
        self.assertIn("function foo() { ... }", result)

if __name__ == "__main__":
    unittest.main()
