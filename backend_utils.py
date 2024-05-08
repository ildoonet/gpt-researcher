import re
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from searchweb import get_htmls, get_content


def parse_context(context):
    # 정규 표현식을 이용해 타이틀, 소스 및 콘텐츠 추출
    pattern = r"Source:\s*(https?://\S+)\nTitle:\s*(.+?)\nContent:\s*(.+?)(?=\Source:|\Z)"
    matches = re.findall(pattern, context, re.DOTALL)

    # 각 매치 결과를 JSON 형식으로 변환
    articles = [{"Title": match[1], "Source": match[0], "Content": match[2]} for match in matches]
    return articles


def relevant_section(key, url, title, document):
    # 텍스트를 섹션으로 나누기 위해 RecursiveCharacterTextSplitter 사용
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    sections = text_splitter.split_text(document)

    # 임베딩 생성
    embeddings = OpenAIEmbeddings()

    # 벡터 데이터 저장소 생성
    db = FAISS.from_texts(sections, embeddings)

    docs = db.similarity_search(key)

    # getting Title
    htmls = get_htmls([url])
    if len(htmls) > 0:
        html = htmls[0]
        try:
            title, img_src, _ = get_content(html[1], url)
        except:
            title = ''
            img_src = ''
    else:
        img_src = ''

    return title, img_src, docs[0].page_content