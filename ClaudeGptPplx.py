!pip install openai

ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"  # Replace with your Anthropic API key
OPENAI_API_KEY = "OPENAI_API_KEY" # Replace with your OpenAI API key
PPLX_API_KEY = "PERPLEXITY_API_KEY" # Replace with your Perplexity API key

import requests
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_claude_step_1(prompt, model="claude-3-opus-20240229", max_tokens=2000, temperature=0.1): # using 0.1 for precision during the pre-answer phase
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": "You are a world-class expert across every topic. Answer with incredibly accurate and useful responses.",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    print(response.json())
    return response.json()['content'][0]['text']



def generate_gpt_step_1(prompt, model="gpt-4", max_tokens=2000, temperature=0.1): # using 0.1 for precision during the pre-answer phase
  response = client.chat.completions.create(
    model=model,
    messages=[
      {
        "role": "system",
        "content": "You are a world-class expert across every topic. Answer with incredibly accurate and useful responses."
      },
      {
        "role": "user",
        "content": prompt,
      }
    ],
    max_tokens=max_tokens,
    temperature=temperature,
  )

  return response.choices[0].message.content



def generate_perplexity_step_1(prompt, model="pplx-70b-online", max_tokens=2000, temperature=0.1): # using 0.1 for precision during the pre-answer phase
  payload = {
      "model": model,
      "messages": [
          {
              "role": "system",
              "content": "Be precise."
          },
          {
              "role": "user",
              "content": prompt,
          }
      ]
  }
  headers = {
      "accept": "application/json",
      "content-type": "application/json",
      "Authorization": f"Bearer {PPLX_API_KEY}"
  }

  response = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers)
  print(response.json())

  return response.json()['choices'][0]['message']['content']


def generate_claude_step_2(question, claude_answer, gpt_answer, pplx_answer, model="claude-3-opus-20240229", max_tokens=2000, temperature=0.6): # using 0.6 for flowiness during the answer phase
    prompt = f"""Here is the user's question:
<user_question>
{question}
</user_question>

<ai_answers_to_inform_your_response>
GPT-4, which is strong at reasoning, responded with:
<gpt_4_response>
{gpt_answer}
</gpt_4_response>

Claude 3, which is strong at reasoning and has a great personality, responded with:
<claude_3_response>
{claude_answer}
</claude_3_response>

PPLX AI, which is weaker at reasoning but has access to up-to-date information from the internet, responded with:
<pplx_response>
{pplx_answer}
</pplx_response>
</ai_answers_to_inform_your_response>

Again, the user's question is:
<user_question>
{question}
</user_question>

Use all of these AI answers to inform your final answer. Now, answer the user's question perfectly."""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": "The user has asked a question, and we've asked three different LLMs to response. You will take all of their outputs, and combine their strengths and mitigate their mistakes into a final, perfect answer.",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    print(response.json())
    return response.json()['content'][0]['text']

def generate_response(question):

  claude = generate_claude_step_1(question)
  gpt = generate_gpt_step_1(question)
  pplx = generate_perplexity_step_1(question)

  final = generate_claude_step_2(question, claude, gpt, pplx)

  return final, claude, gpt, pplx


question = "What is today's news?"

response = generate_response(question)

print('\n\n', response[0])
