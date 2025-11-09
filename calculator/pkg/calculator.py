import re
import math

class Calculator:
    def __init__(self):
        self.operators = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b if b != 0 else float('inf'),
            "%": lambda a, b: a % b if b != 0 else float('nan'),
            "^": lambda a, b: a ** b,
            "**": lambda a, b: a ** b,
        }
        self.precedence = {
            "+": 1,
            "-": 1,
            "*": 2,
            "/": 2,
            "%": 2,
            "^": 3,
            "**": 3,
        }
        self.right_associative = {"^", "**"}

    def evaluate(self, expression):
        """
        Evaluate a mathematical expression.
        
        Supports:
        - Basic arithmetic: +, -, *, /
        - Modulo: %
        - Exponentiation: ^ or **
        - Parentheses: ()
        - Negative numbers: -5, -3.14
        - Decimal numbers: 3.14, 0.5
        
        Args:
            expression: String containing the mathematical expression
            
        Returns:
            float: The result of the calculation
            
        Raises:
            ValueError: If the expression is invalid or empty
            ZeroDivisionError: If division by zero occurs
        """
        if not expression or expression.isspace():
            raise ValueError("Expression is empty or contains only whitespace.")
        
        # Clean the expression - remove whitespace
        expression = re.sub(r'\s+', '', expression)
        
        # Tokenize the expression: separate numbers, operators, and parentheses
        # Handle negative numbers by converting unary minus to (0 - number)
        tokens = []
        i = 0
        while i < len(expression):
            if expression[i].isdigit() or expression[i] == '.':
                # Parse number (including decimal)
                num_str = ''
                while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                    num_str += expression[i]
                    i += 1
                tokens.append(num_str)
                continue
            elif expression[i] == '-' and (not tokens or tokens[-1] in '+-*/%^(' or tokens[-1] == '**'):
                # This is a unary minus - convert to (0 - number)
                tokens.append('(')
                tokens.append('0')
                tokens.append('-')
                i += 1
                # Parse the number that follows
                if i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                    num_str = ''
                    while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                        num_str += expression[i]
                        i += 1
                    tokens.append(num_str)
                    tokens.append(')')
                else:
                    raise ValueError("Unary minus must be followed by a number")
                continue
            elif expression[i:i+2] == '**':
                tokens.append('**')
                i += 2
            else:
                tokens.append(expression[i])
                i += 1
        
        if not tokens:
            raise ValueError("No valid tokens found in expression.")
        
        return self._evaluate_infix(tokens)

    def _evaluate_infix(self, tokens):
        """Evaluate infix expression using Shunting Yard algorithm."""
        values = []
        operators = []
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            # Handle numbers
            if self._is_number(token):
                values.append(float(token))
            
            # Handle opening parenthesis
            elif token == '(':
                operators.append(token)
            
            # Handle closing parenthesis
            elif token == ')':
                while operators and operators[-1] != '(':
                    self._apply_operator(operators, values)
                if not operators or operators[-1] != '(':
                    raise ValueError("Mismatched parentheses")
                operators.pop()  # Remove '('
            
            # Handle operators
            elif token in self.operators:
                # Handle operator precedence and associativity
                while (
                    operators
                    and operators[-1] != '('
                    and operators[-1] in self.operators
                    and (
                        (token in self.right_associative and 
                         self.precedence[operators[-1]] > self.precedence[token])
                        or
                        (token not in self.right_associative and
                         self.precedence[operators[-1]] >= self.precedence[token])
                    )
                ):
                    self._apply_operator(operators, values)
                operators.append(token)
            
            else:
                raise ValueError(f"Invalid token: {token}")
            
            i += 1
        
        # Apply remaining operators
        while operators:
            if operators[-1] == '(':
                raise ValueError("Mismatched parentheses")
            self._apply_operator(operators, values)
        
        if len(values) != 1:
            raise ValueError(f"Invalid expression: {len(values)} values remaining")
        
        result = values[0]
        
        # Check for special values
        if math.isinf(result):
            raise ZeroDivisionError("Division by zero")
        if math.isnan(result):
            raise ValueError("Invalid operation (e.g., modulo by zero)")
        
        return result

    def _is_number(self, token):
        """Check if a token is a number."""
        try:
            float(token)
            return True
        except ValueError:
            return False

    def _apply_operator(self, operators, values):
        """Apply an operator to the top two values on the stack."""
        if not operators:
            return
        
        operator = operators.pop()
        if len(values) < 2:
            raise ValueError(f"Not enough operands for operator {operator}")
        
        b = values.pop()
        a = values.pop()
        
        try:
            result = self.operators[operator](a, b)
            values.append(result)
        except ZeroDivisionError:
            raise ZeroDivisionError(f"Division by zero in operation: {a} {operator} {b}")
        except Exception as e:
            raise ValueError(f"Error applying operator {operator}: {str(e)}")
