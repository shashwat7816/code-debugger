from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure the API key
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyD6bTQ1NbxvKaIfybTWxcjS8epl1tYQufc")
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)

# Programming languages supported
LANGUAGES = ["Python", "Java", "C++", "JavaScript", "C#", "Go", "Rust", "PHP", "Swift", "TypeScript", "Kotlin", "Ruby"]

# Debugging modes
DEBUG_MODES = ["Standard Debugging", "Performance Analysis", "Security Review", "Code Explanation"]

def format_bot_response(response, language):
    """Format the bot's response to highlight code blocks and explanations"""
    formatted_text = ""
    lines = response.split('\n')
    in_code_block = False
    code_block = []
    
    for line in lines:
        # Check for code block markers ```
        if line.strip().startswith('```') or line.strip() == '```':
            if in_code_block:
                # End of code block
                formatted_text += "\n<div class='code-block'>\n"
                code_text = "\n".join(code_block)
                formatted_text += code_text + "\n"
                formatted_text += "</div>\n\n"
                code_block = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
            continue
        
        if in_code_block:
            # Collect code block lines
            code_block.append(line)
        else:
            # Regular text - check for special formatting
            if line.strip().startswith('#') or line.strip().startswith('##'):
                # Heading
                formatted_text += f"<h3>{line}</h3>\n"
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                # List item
                formatted_text += f"<li>{line[2:]}</li>\n"
            elif "ERROR" in line.upper() or "ISSUE" in line.upper():
                # Error or issue description
                formatted_text += f"<div class='error'>{line}</div>\n"
            elif "FIXED" in line.upper() or "SOLUTION" in line.upper():
                # Solution or fix
                formatted_text += f"<div class='success'>{line}</div>\n"
            else:
                # Regular explanation text
                formatted_text += f"{line}\n"
    
    # Handle any remaining code block
    if code_block:
        formatted_text += "\n<div class='code-block'>\n"
        code_text = "\n".join(code_block)
        formatted_text += code_text + "\n"
        formatted_text += "</div>\n\n"
    
    return formatted_text

def get_debugging_response(user_input, language, mode="Standard Debugging"):
    """Send the user's input code & language to Gemini AI for debugging."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest") 
        
        # Different prompts based on mode
        if mode == "Standard Debugging":
            prompt = f"""Debug this {language} code:
```{language}
{user_input}
```

Please provide:
1. A clear explanation of any issues found
2. The corrected code blocks using markdown triple backticks
3. Explanations of why the fixes work
"""
        elif mode == "Performance Analysis":
            prompt = f"""Analyze this {language} code for performance issues:
```{language}
{user_input}
```

Please provide:
1. Performance bottlenecks identified
2. Optimized code blocks using markdown triple backticks
3. Explanation of how the optimizations improve performance
"""
        elif mode == "Security Review":
            prompt = f"""Review this {language} code for security vulnerabilities:
```{language}
{user_input}
```

Please provide:
1. Security issues identified
2. Secure code alternatives using markdown triple backticks
3. Explanation of the security risks and how the fixes address them
"""
        elif mode == "Code Explanation":
            prompt = f"""Explain this {language} code in simple terms:
```{language}
{user_input}
```

Please provide:
1. A high-level overview of what this code does
2. A step-by-step breakdown of key sections (with code snippets in triple backticks)
3. Explanations of any complex or important concepts
"""
        else:
            # Fallback to standard debugging
            prompt = f"Debug this {language} code:\n{user_input}\nProvide fixes and explanations."
            
        response = model.generate_content(prompt)
        raw_text = response.text if response.text else "No response from AI."
        formatted_text = format_bot_response(raw_text, language)
        return formatted_text
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES, debug_modes=DEBUG_MODES)

@app.route('/api/debug', methods=['POST'])
def debug_code():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'Python')
    mode = data.get('mode', 'Standard Debugging')
    
    if not code.strip():
        return jsonify({'error': 'No code provided'})
    
    response = get_debugging_response(code, language, mode)
    return jsonify({'response': response})

# Health check endpoint for Vercel
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)
