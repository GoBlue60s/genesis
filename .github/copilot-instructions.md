## General Principles
- Write code that is **readable, maintainable, and well-structured**.
- Follow the **DRY (Don't repeat yourself) principle** to avoid redundancy.
- Use **descriptive variable and function names** 
  (e.g. "caluculate_total" instead of "calc").
- Keep code **simple and concise** while ensuring clarity-
  **avoid over-engineering**.
- Use double quotes for **string literals**

## PEP 8 Compliance
- **Indentation** Use **2 spaces** per indentation level. No tabs.
- **Line length** - limit lines to **79 characters**. 
  Use Parentheses (not backslashes) for line continuation.
- **Blank lines:**
 - **2 blank lines** before top level function and class definitions.
- **Whitespace:**
 - Add **one space** after commas ('func(a, b)' not 'func(a,b)').
 - Avoid extra whitespace inside parentheses ('(x + y)' not '( x + y )').
 - Use spaces around operators ('x = 5 + 3' not 'x=5+3').
- **Naming Conventions:**
 - **functions & variables:** 'snake case' (e.g., 'get_user_data').
  - **Classes:** 'PascalCase' (e.g., 'DataProcessor').
  - **Constants:** 'UPPER_CASE' (e.g., 'MAX_RETRIES').
  - **Avoid** single-letter variable names even as the index of a loop.
## Code Structure
- **Imports:** Place imports at the **top**.
- **Main block** Use 'if __name__ == "__main__":' 
  to prevent code from running on import.
- **functions:**
 - Include a **docstring** explaining purpose, paramters, and return value.
  - Keep functions **focused**- do **one thing well**.
   - Limit function length to **20-30 lines** where possible.
  - **Return statements** should **never** contain expressions, only variables. 
- **Classes:**
 - Use  **Classes** when data and behavior are closely related.
 - Include an **'__init__' method** with **clear parameter names**.
 - Add a **class-level docstring** explaining its purpose.


## Type Hints
- Use **type hints** to improve clarity.

## Error Handling
- Use "try/except" blocks to handle exceptions gracefully.
- Catch **specific exceptions** (e.g., "ValueError") rather than gneral ones.
- Include **meaningful error messages**.

## Comments
- **Explain why**, not just **what**.
- Keep comments **concise and relevant**.
- Avoid **redundant** comments. (e.g., '# Set x to 5' above 'x = 5').
- Use **inline comments sparingly** and align them.

## Additional Best Practices
- **Avoid global variables** -pass data via parmters.
- Test **edge cases** mentally and mention them in your explanation 
  if they're critical.