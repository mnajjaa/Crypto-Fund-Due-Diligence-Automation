import ollama
from . import sys_msgs
import requests
import trafilatura
from bs4 import BeautifulSoup
import os
from exa_py import Exa
from dotenv import load_dotenv


EXA_API_KEY="6ad823fd-4ca5-4913-8901-a10a54899f80"

assistant_convo = [sys_msgs.assistant_msg]

def query_generator(prompt):
    sys_msg = sys_msgs.query_msg
    query_msg = f'CREATE A SEARCH QUERY FOR THIS PROMPT: \n{prompt}'

    response = ollama.chat(
        model="llama3",
        messages=[
            {'role': 'system', 'content': sys_msg},
            {'role': 'user', 'content': query_msg}
        ]
    )

    return response['message']['content']

load_dotenv()

def exa_search_with_contents(query, num_results=10):
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY environment variable not set")

    exa = Exa(api_key)

    search_response = exa.search_and_contents(
        query=query,
        num_results=num_results,
        text=True,
        type="auto"
    )

    results = []
    for i, result in enumerate(search_response.results, start=1):
        results.append({
            'id': i,
            'link': result.url,
            'title': result.title,
            'search_description': result.text[:200] + "..." if result.text else 'No description available'
        })
    print(f"EXA Search Results: {len(results)} results found.")
    return results

def best_search_result(s_results, query, prompt):
    sys_msg = sys_msgs.best_search_msg
    best_msg = f'SEARCH_RESULTS: {s_results}\nUSER_PROMPT: {prompt}\nSEARCH_QUERY: {query}'

    for _ in range(2):
        try:
            response = ollama.chat(
                model="llama3",
                messages=[
                    {'role': 'system', 'content': sys_msg},
                    {'role': 'user', 'content': best_msg}
                ]
            )
            print(int(response['message']['content']))
            return int(response['message']['content'])
        except:
            continue

def scrape_webpage(url):
    try:
        downloaded = trafilatura.fetch_url(url=url)
        return trafilatura.extract(downloaded, include_formatting=True, include_links=True)
    except Exception:
        return None

def classify_question_type(query):
    classification_prompt = f"""You are a classification assistant.

Decide if the following question requires a short, direct answer (like a number, name, or fact), or a detailed, multi-paragraph summary.

Respond with only one word: `short` or `detailed`.

### Question:
{query}

### Answer Style:"""

    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': classification_prompt}],
            stream=False
        )

        style = response.get('message', {}).get('content', '').strip().lower()
        return "short" if "short" in style else "detailed"

    except Exception as e:
        print(f"[Classification failed]: {e}")
        return "detailed"  # Default to detailed if error

def contains_data_needed(search_content, query, prompt):
    sys_msg = sys_msgs.contains_data_msg
    needed_prompt = f'PAGE_TEXT: {search_content}\nUSER_PROMPT: {prompt}\nSEARCH_QUERY: {query}'

    response = ollama.chat(
        model="llama3",
        messages=[
            {'role': 'system', 'content': sys_msg},
            {'role': 'user', 'content': needed_prompt}
        ]
    )

    content = response['message']['content']
    print(f"Contains data needed: {content}")
    return 'true' in content.lower()

def ai_search(prompt):
    context = None
    print('GENERATING SEARCH QUERY.')
    search_query = query_generator(prompt)

    if search_query.startswith('"'):
        search_query = search_query[1:-1]

    search_results = exa_search_with_contents(search_query)
    context_found = False

    while not context_found and len(search_results) > 0:
        best_result = best_search_result(
            s_results=search_results, query=search_query, prompt=prompt)

        try:
            page_link = search_results[best_result]['link']
        except:
            print('FAILED TO SELECT BEST SEARCH RESULT, TRYING AGAIN.')
            continue

        page_text = scrape_webpage(page_link)
        if page_text and isinstance(page_text, str):
            print(f"✅ First 500 chars of scraped text:\n{page_text[:500]}...\n")
        else:
            print("❌ No text found or invalid type.")

        search_results.pop(best_result)

        if page_text and contains_data_needed(search_content=page_text, query=search_query, prompt=prompt):
            context = page_text
            context_found = True

    return context

def stream_assistant_response():
    global assistant_convo
    response_stream = ollama.chat(
        model='llama3', messages=assistant_convo, stream=True)
    complete_response = ''

    print('ASSISTANT: ', end='')

    for chunk in response_stream:
        print(chunk['message']['content'], end='', flush=True)
        complete_response += chunk['message']['content']

    assistant_convo.append({'role': 'assistant', 'content': complete_response})
    print('\n\n')

def main(prompt):
    global assistant_convo

    print(f'USER (hardcoded): {prompt}\n')
    assistant_convo.append({'role': 'user', 'content': prompt})

    context = ai_search(prompt)
    assistant_convo = assistant_convo[:-1]  # Remove temp user message

    classification_response = classify_question_type(prompt)
    print(f'Classification: {classification_response}')

    if context:
        if classification_response == "short":
            final_prompt = f'''CONTEXT (only answer based on this, do not guess):
{context}

USER PROMPT:
{prompt}

Important Instructions:
- Provide a short, direct, factual answer based strictly on the CONTEXT.
- If the answer is not found or is outdated by more than a few days, reply:
"The information is not available in the provided context."
- Do not guess, assume, or fabricate missing information.
'''
        else:
            final_prompt = f'''CONTEXT (only answer based on this, do not guess):
{context}

USER PROMPT:
{prompt}

Important Instructions:
- Provide a detailed, multi-paragraph response based strictly on the CONTEXT.
- If the answer is not clearly found in CONTEXT, reply exactly:
"The information is not available in the provided context."
- Do not guess, assume, or fabricate missing information.
'''
    else:
        final_prompt = (
            f'USER PROMPT: {prompt}\n\nFAILED SEARCH:\n'
            'The AI search model was unable to extract reliable data. '
            'Ask the user if they would like you to search again or proceed without web search context.'
        )

    assistant_convo.append({'role': 'user', 'content': final_prompt})
    stream_assistant_response()

if __name__ == '__main__':
    main("what is the founders and co founders of etherium  ?")
