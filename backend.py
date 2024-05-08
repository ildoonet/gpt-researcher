from backend_utils import parse_context, relevant_section
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import timedelta
import json
import asyncio
from gpt_researcher.master.agent import GPTResearcher
from gpt_researcher.utils.enum import ReportType
from gpt_researcher.llm_provider import GroqProvider
from redis import Redis
from rq import Queue
import time

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)


def convert_context(contexts):
    for k, v in contexts.items():
        contexts[k] = parse_context(v)

    q = Queue(connection=Redis())

    # getting relavant section from the context
    jobs = []
    for key, value in contexts.items():
        for article in value:
            # article['Relavant'] = relevant_section(key, article['Content'])
            # del article['Content']
            job = q.enqueue(relevant_section, key, article['Source'], article['Title'], article['Content'])
            jobs.append(job)
    
    i = 0
    success = 0
    while success < len(jobs):
        i = success = 0
        for key, value in contexts.items():
            for article in value:
                if jobs[i].is_finished:
                    article['Title'], article['Image'], article['Relavant'] = jobs[i].return_value()
                    success += 1
                i += 1
        # print(success, len(jobs))
        time.sleep(0.5)

    new_contexts = {}
    url_set = set()
    for key, value in contexts.items():
        new_contexts[key] = []
        for article in value:
            if article['Source'] not in url_set:
                new_contexts[key].append(article)
                url_set.add(article['Source'])

    return new_contexts


@app.route('/api/research')
def research():
    query = request.args.get('q')
    isPro = int(request.args.get('pro', 0))
    if not query:
        return jsonify({'error': 'Query parameter is missing'}), 400

    def gen_research(query):
        r = GPTResearcher(
            query=query, 
            report_type=ReportType.DetailedReport.value if isPro else ReportType.ResearchReport.value,
            source_urls=None,
            config_path='backend.json'
        )
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(r.conduct_research())
        # with open('backend.response1.json', 'w') as f:
        #     f.write(json.dumps({'contexts': r.context_by_query}))

        report = loop.run_until_complete(r.write_report())
        loop.close()
        # with open('backend.response2.json', 'w') as f:
        #     f.write(json.dumps({'report': report}))
        yield 'data: ' + json.dumps({'report': report}) + '\n\n'

        yield 'data: ' + json.dumps({'contexts': convert_context(r.context_by_query)}) + '\n\n'

    return Response(gen_research(query), mimetype='text/event-stream')

@app.route('/api/test')
def test():
    def gen_test():
        with open('backend.response1.json', 'r') as f:
            response1 = json.load(f)
        response1 = {'contexts': convert_context(response1['contexts'])}
        yield 'data: ' + json.dumps(response1) + '\n\n'
        with open('backend.response2.json', 'r') as f:
            response2 = json.load(f)
        yield 'data: ' + json.dumps(response2) + '\n\n'
    return Response(gen_test(), mimetype='text/event-stream')

@app.route('/api/response')
def response():
    query = request.args.get('q')

    groq = GroqProvider('llama3-8b-8192', 0.1, 600)
    messages = [
        {
            "role": "system",
            "content": "You are the search assistant by LLM. The assistant suggests question queries to help you find the information you need. You can ask the assistant to search for information on a specific topic. Also the assistant generates summarized research response to your queries. Please response in JSON Format as below conversations."
        },
        {
            "role": "user",
            "content": "OpenAI"
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "query": ['latest news on OpenAI', 'OpenAI funding', 'OpenAI research', 'OpenAI projects', 'OpenAI team', 'OpenAI products', 'OpenAI services', 'OpenAI competitors', 'OpenAI controversies', 'OpenAI future'],
                "response": """OpenAI is an artificial intelligence research laboratory consisting of the for-profit OpenAI LP and the non-profit OpenAI Inc. The company aims to ensure that artificial general intelligence benefits all of humanity. 
                - OpenAI Overview
                - OpenAI Funding
                - OpenAI Research / Projects
                - OpenAI Team"""
            })
        },
        {
            "role": "user",
            "content": query
        }
    ]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    content = loop.run_until_complete(groq.get_chat_response(messages, False))
    loop.close()
    return jsonify({'response': content})


if __name__ == '__main__':
    app.run(debug=True, port=8080)
