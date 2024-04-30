"""
expression = term { ("+" | "-") term } 
term = factor { ("*" | "/" | "%") factor } # Added modulus symbol to grammer
factor = number | "(" expression ")" | "-" factor | "!" # Unary Negation added here
number = <number>
"""
def create_node(tag, left=None, right=None, value=None):
    return {"tag": tag, "value": value, "left": left, "right": right}


def parse_expression(tokens):
    node, tokens = parse_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_term(tokens[1:])
        node = create_node(tag, left=node, right=right_node)
    return node, tokens


def parse_term(tokens):
    node, tokens = parse_factor(tokens)
    while tokens[0]["tag"] in ["*", "/","%"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_factor(tokens[1:])
        node = create_node(tag, left=node, right=right_node)
    return node, tokens


def parse_factor(tokens):
    token = tokens[0]
    tag = token["tag"]
    if tag == "number":
        return create_node("number", value=token["value"]), tokens[1:]
    if tag == "(":
        node, tokens = parse_expression(tokens[1:])
        if tokens and tokens[0]["tag"] != ")":
            raise Exception("Expected ')'")
        return node, tokens[1:]
    if tag == "-": # Look for negation
        node, tokens = parse_factor(tokens[1:])
        return create_node("negate", left = node), tokens
    raise Exception(f"Unexpected token: {tokens[0]}")


def parse(tokens):
    tokens.append({"tag": None})  # Sentinel to mark the end of input
    ast, _ = parse_expression(tokens)
    return ast


def format(ast, indent=0):
    indentation = " " * indent
    if ast["tag"] in ["number"]:
        return indentation + str(ast["value"])
    result = indentation + ast["tag"]
    if ast["left"]:
        result = result + "\n" + format(ast["left"], indent=indent + 4)
    if ast["right"]:
        result = result + "\n" + format(ast["right"], indent=indent + 4)
    return result


from tokenizer import tokenize


def test_simple_addition_parsing():
    print("test simple addition parsing...")
    tokens = tokenize("1+2")
    ast = parse(tokens)
    assert ast == {
        "tag": "+",
        "value": None,
        "left": {"tag": "number", "value": 1, "left": None, "right": None},
        "right": {"tag": "number", "value": 2, "left": None, "right": None},
    }

def test_simple_modulus_parsing(): # Added test for modulus parsing
    print("test simple modulus parsing...")
    tokens = tokenize("10 % 3")
    ast = parse(tokens)
    assert ast == {
        "tag": "%",
        "value": None,
        "left": {"tag": "number", "value": 10, "left": None, "right": None},
        "right": {"tag": "number", "value": 3, "left": None, "right": None},
    }

def test_unary_negation_parsing(): # Test for unary negation
    print("testing unary negation parsing...")
    tokens = tokenize("1+-2")
    ast = parse(tokens)
    assert ast == {
       "tag": "+",
       "value": None,
       "left": {"tag": "number", "value": 1, "left": None, "right": None},
        "right":{
           "tag": "negate",
           "value": None,
           "left": {"tag": "number","value": 2,"left": None,"right": None},
            "right": None
        }
    }

def test_nested_expressions_parsing():
    print("test nested expressions parsing...")
    tokens = tokenize("(1+2)*3")
    ast = parse(tokens)
    assert ast == {
        "tag": "*",
        "value": None,
        "left": {
            "tag": "+",
            "value": None,
            "left": {"tag": "number", "value": 1, "left": None, "right": None},
            "right": {"tag": "number", "value": 2, "left": None, "right": None},
        },
        "right": {"tag": "number", "value": 3, "left": None, "right": None},
    }


def test_operation_precedence_parsing():
    print("test operation precedence parsing...")
    tokens = tokenize("4-2/1")
    ast = parse(tokens)
    assert ast == {
        "tag": "-",
        "value": None,
        "left": {"tag": "number", "value": 4, "left": None, "right": None},
        "right": {
            "tag": "/",
            "value": None,
            "left": {"tag": "number", "value": 2, "left": None, "right": None},
            "right": {"tag": "number", "value": 1, "left": None, "right": None},
        },
    }


def test_format_ast():
    print("test format AST...")
    ast = {
        "tag": "-",
        "value": None,
        "left": {"tag": "number", "value": 4, "left": None, "right": None},
        "right": {
            "tag": "/",
            "value": None,
            "left": {"tag": "number", "value": 2, "left": None, "right": None},
            "right": {"tag": "number", "value": 1, "left": None, "right": None},
        },
    }
    result = format(ast)
    assert result == "-\n    4\n    /\n        2\n        1"


if __name__ == "__main__":
    test_simple_addition_parsing()
    test_simple_modulus_parsing() # Added test for modulus parsing
    test_unary_negation_parsing() # Added test for negation parsing
    test_nested_expressions_parsing()
    test_operation_precedence_parsing()
    test_format_ast()
    print("done.")
