# 📝 Prompt Engineering - Cheat Sheet

## 📚 Key Concepts

### 1. **Core Principles**
```
Principle 1: Write clear and specific instructions
Principle 2: Give the model time to think
```

## 💡 Prompting Techniques

### 1. **Basic Prompting**
```python
prompt = "Translate this to French: Hello, how are you?"
```

### 2. **Few-Shot Prompting**
```python
prompt = """
Translate English to French:

English: Hello
French: Bonjour

English: Goodbye
French: Au revoir

English: Thank you
French: """
```

### 3. **Chain-of-Thought (CoT)**
```python
prompt = """
Analyze this step-by-step:

Step 1: Identify the problem
Step 2: Consider the context
Step 3: Reason through the solution
Step 4: Provide the answer
"""
```

### 4. **Role-Based Prompting**
```python
prompt = """
You are an expert shipping logistics analyst with 15 years of experience.

Analyze this shipment delay and provide recommendations.
"""
```

### 5. **Structured Output**
```python
prompt = """
Analyze the sentiment and provide output in this JSON format:
{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "key_points": ["point1", "point2"]
}
"""
```

### 6. **Delimiters for Clarity**
```python
prompt = """
Summarize the text below, delimited by triple backticks.

```
[Long text here]
```
"""
```

## 🔑 Important Files

| File | Purpose |
|------|---------|
| `prompting.py` | Basic prompting techniques |
| `tactics_prompting.py` | Advanced tactics |
| `cot_prompting.py` | Chain-of-thought examples |
| `rgboc.py` | Role/Goal/Background/Output/Context pattern |
| `digitalise_pdf.py` | Extract text from PDFs |
| `digitalise_image.py` | Extract text from images (OCR) |
| `exercise_1_customer_sentiment_analyzer.py` | Sentiment analysis |
| `exercise_2_booking_validator.py` | Validation with prompts |

## 🎯 RGBOC Framework

```python
prompt = """
Role: You are a customer service quality analyst

Goal: Analyze this call transcript and classify urgency

Background: This is from a shipping company's support line.
We need to identify high-priority issues requiring escalation.

Output Format:
{
    "urgency": "low/medium/high",
    "escalate": true/false,
    "reason": "explanation"
}

Context: Customer has been waiting 5 days for shipment
[Call transcript here]
"""
```

## 💭 Prompt Engineering Tactics

### Tactic 1: Use Delimiters
```python
# ✅ Clear structure
prompt = f"""
Text: ```{user_text}```
Task: Summarize
"""

# ❌ Ambiguous
prompt = f"Summarize {user_text}"
```

### Tactic 2: Ask for Structured Output
```python
prompt = """
Provide output as a Python dictionary:
{
    "name": "value",
    "score": 0.8
}
"""
```

### Tactic 3: Check Conditions
```python
prompt = """
If the text contains customer complaints, analyze sentiment.
If not, just say "No complaints found".
"""
```

### Tactic 4: Few-Shot Learning
```python
prompt = """
Example 1:
Input: "Great service!"
Output: Positive

Example 2:
Input: "Terrible delay"
Output: Negative

Now analyze:
Input: "Container arrived on time"
Output:
"""
```

### Tactic 5: Give Time to Think (CoT)
```python
prompt = """
Let's solve this step-by-step:

1. First, identify...
2. Then, analyze...
3. Finally, conclude...
"""
```

### Tactic 6: Specify Length
```python
prompt = "Summarize in 50 words or less"
prompt = "Explain in 3 bullet points"
```

## 🚨 Common Mistakes

### 1. Vague Instructions
```python
# ❌ Too vague
"Tell me about this"

# ✅ Specific
"Summarize the key business risks mentioned in this contract in 3 bullet points"
```

### 2. No Examples
```python
# ❌ Abstract
"Classify the sentiment"

# ✅ With examples
"Classify as Positive, Negative, or Neutral. Example: 'Great!' = Positive"
```

### 3. Not Specifying Format
```python
# ❌ Format unclear
"Extract dates"

# ✅ Format specified
"Extract all dates in YYYY-MM-DD format as a JSON array"
```

### 4. Forgetting Edge Cases
```python
# ✅ Handle edge cases
"If no dates are found, return an empty array []"
```

## 📊 Temperature Settings

```python
temperature=0.0   # Deterministic, consistent (for analysis, extraction)
temperature=0.3   # Mostly focused (for classification)
temperature=0.7   # Balanced (default for most tasks)
temperature=1.0   # Creative, varied (for content generation)
temperature=1.5   # Very creative (for brainstorming)
```

## 🎓 Real-World Use Cases

### Customer Service Analysis
```python
prompt = """
Analyze this customer call transcript and identify:
1. Sentiment (positive/negative/neutral)
2. Urgency level (low/medium/high)
3. Key issues mentioned
4. Whether escalation is needed

Transcript:
```{transcript}```
"""
```

### Document Processing
```python
prompt = """
Extract the following from this invoice:
- Invoice number
- Date (YYYY-MM-DD)
- Total amount
- Vendor name

Return as JSON.
"""
```

### Data Validation
```python
prompt = """
Validate this booking request:
- Check if date is in future
- Verify container type is valid
- Check if route exists

Return validation errors as a list, or empty list if valid.
"""
```

## 🚀 Quick Start Template

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def get_completion(prompt, model="gpt-4o-mini", temperature=0):
    response = client.responses.create(
        model=model,
        input=prompt,
        temperature=temperature
    )
    return response.output_text

# Use it
prompt = """
Role: Expert analyst
Task: Analyze this data
Output: JSON format
"""

result = get_completion(prompt)
print(result)
```

## 💡 Pro Tips
1. **Iterate**: Start simple, add complexity
2. **Test**: Try multiple examples
3. **Measure**: Track accuracy/quality
4. **Document**: Save successful prompts
5. **Version**: Keep prompt versions for comparison
6. **Benchmark**: Test against baseline

## 🔍 Debugging Prompts
```python
# Add reasoning instructions
"Explain your reasoning before providing the answer"

# Request confidence
"Rate your confidence from 0-1"

# Ask for alternatives
"Provide top 3 possible answers"
```
