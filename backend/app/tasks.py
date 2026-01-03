"""Task definitions for the LLM Among Us game."""

TASK_1 = {
    "id": "fizzbuzz",
    "title": "FizzBuzz",
    "functionName": "fizzbuzz",
    "description": """Write a function fizzbuzz(n) that returns a list of strings from 1 to n where:
- Numbers divisible by 3 are replaced with "Fizz"
- Numbers divisible by 5 are replaced with "Buzz"  
- Numbers divisible by both 3 and 5 are replaced with "FizzBuzz"
- Other numbers are converted to strings

Example: fizzbuzz(5) returns ["1", "2", "Fizz", "4", "Buzz"]""",
    "examples": [
        {"input": "fizzbuzz(5)", "output": '["1", "2", "Fizz", "4", "Buzz"]'},
        {
            "input": "fizzbuzz(15)",
            "output": '["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]',
        },
    ],
    "test_cases": [
        {"input": [1], "expected": ["1"]},
        {"input": [3], "expected": ["1", "2", "Fizz"]},
        {"input": [5], "expected": ["1", "2", "Fizz", "4", "Buzz"]},
        {
            "input": [15],
            "expected": [
                "1",
                "2",
                "Fizz",
                "4",
                "Buzz",
                "Fizz",
                "7",
                "8",
                "Fizz",
                "Buzz",
                "11",
                "Fizz",
                "13",
                "14",
                "FizzBuzz",
            ],
        },
        {"input": [0], "expected": []},
        {
            "input": [16],
            "expected": [
                "1",
                "2",
                "Fizz",
                "4",
                "Buzz",
                "Fizz",
                "7",
                "8",
                "Fizz",
                "Buzz",
                "11",
                "Fizz",
                "13",
                "14",
                "FizzBuzz",
                "16",
            ],
        },
    ],
}

TASK_2 = {
    "id": "palindrome",
    "title": "Valid Palindrome",
    "functionName": "is_palindrome",
    "description": """Write a function is_palindrome(s) that returns True if the string is a palindrome, considering only alphanumeric characters and ignoring case.

Example: is_palindrome("A man, a plan, a canal: Panama") returns True
Example: is_palindrome("race a car") returns False
Example: is_palindrome("") returns True""",
    "examples": [
        {"input": 'is_palindrome("A man, a plan, a canal: Panama")', "output": "True"},
        {"input": 'is_palindrome("race a car")', "output": "False"},
        {"input": 'is_palindrome("")', "output": "True"},
    ],
    "test_cases": [
        {"input": ["A man, a plan, a canal: Panama"], "expected": True},
        {"input": ["race a car"], "expected": False},
        {"input": [""], "expected": True},
        {"input": [" "], "expected": True},
        {"input": ["a"], "expected": True},
        {"input": ["Aa"], "expected": True},
        {"input": ["0P"], "expected": False},
        {"input": ["ab_a"], "expected": True},
        {"input": ["123321"], "expected": True},
        {"input": ["A1b2B1a"], "expected": True},
    ],
}

TASK_3 = {
    "id": "duplicates",
    "title": "Find Duplicates",
    "functionName": "find_duplicates",
    "description": """Write a function find_duplicates(nums) that takes a list of integers and returns a sorted list of all elements that appear more than once.

Example: find_duplicates([1, 2, 3, 2, 4, 3]) returns [2, 3]
Example: find_duplicates([1, 2, 3]) returns []
Example: find_duplicates([1, 1, 1]) returns [1]""",
    "examples": [
        {"input": "find_duplicates([1, 2, 3, 2, 4, 3])", "output": "[2, 3]"},
        {"input": "find_duplicates([1, 2, 3])", "output": "[]"},
        {"input": "find_duplicates([1, 1, 1])", "output": "[1]"},
    ],
    "test_cases": [
        {"input": [[1, 2, 3, 2, 4, 3]], "expected": [2, 3]},
        {"input": [[1, 2, 3]], "expected": []},
        {"input": [[]], "expected": []},
        {"input": [[1]], "expected": []},
        {"input": [[1, 1]], "expected": [1]},
        {"input": [[1, 1, 1, 1]], "expected": [1]},
        {"input": [[5, 5, 4, 4, 3, 3]], "expected": [3, 4, 5]},
        {"input": [[-1, -1, 0, 0]], "expected": [-1, 0]},
        {"input": [[1, 2, 2, 3, 3, 3, 4, 4, 4, 4]], "expected": [2, 3, 4]},
    ],
}

TASK_4 = {
    "id": "balanced_parens",
    "title": "Balanced Parentheses",
    "functionName": "is_balanced",
    "description": """Write a function is_balanced(s) that returns True if the string has balanced parentheses, brackets, and braces. Other characters should be ignored.

Pairs: (), [], {}

Example: is_balanced("({[]})") returns True
Example: is_balanced("([)]") returns False
Example: is_balanced("hello(world)") returns True
Example: is_balanced("") returns True""",
    "examples": [
        {"input": 'is_balanced("({[]})")', "output": "True"},
        {"input": 'is_balanced("([)]")', "output": "False"},
        {"input": 'is_balanced("hello(world)")', "output": "True"},
    ],
    "test_cases": [
        {"input": ["({[]})"], "expected": True},
        {"input": ["([)]"], "expected": False},
        {"input": [""], "expected": True},
        {"input": ["hello(world)"], "expected": True},
        {"input": ["("], "expected": False},
        {"input": [")"], "expected": False},
        {"input": ["((()))"], "expected": True},
        {"input": ["{[()]}"], "expected": True},
        {"input": ["{[(])}"], "expected": False},
        {"input": ["abc"], "expected": True},
        {"input": ["({[}])"], "expected": False},
        {"input": ["((((((((((()))))))))))"], "expected": True},
    ],
}

TASK_5 = {
    "id": "roman_to_int",
    "title": "Roman Numeral to Integer",
    "functionName": "roman_to_int",
    "description": """Write a function roman_to_int(s) that converts a Roman numeral string to an integer.

Roman numerals: I=1, V=5, X=10, L=50, C=100, D=500, M=1000

Subtractive notation: IV=4, IX=9, XL=40, XC=90, CD=400, CM=900

Example: roman_to_int("III") returns 3
Example: roman_to_int("IV") returns 4
Example: roman_to_int("MCMXCIV") returns 1994""",
    "examples": [
        {"input": 'roman_to_int("III")', "output": "3"},
        {"input": 'roman_to_int("IV")', "output": "4"},
        {"input": 'roman_to_int("MCMXCIV")', "output": "1994"},
    ],
    "test_cases": [
        {"input": ["I"], "expected": 1},
        {"input": ["III"], "expected": 3},
        {"input": ["IV"], "expected": 4},
        {"input": ["V"], "expected": 5},
        {"input": ["IX"], "expected": 9},
        {"input": ["LVIII"], "expected": 58},
        {"input": ["MCMXCIV"], "expected": 1994},
        {"input": ["MMXXIV"], "expected": 2024},
        {"input": ["CDXLIV"], "expected": 444},
        {"input": ["CMXCIX"], "expected": 999},
        {"input": ["MMMCMXCIX"], "expected": 3999},
    ],
}

TASKS = [TASK_1, TASK_2, TASK_3, TASK_4, TASK_5]
