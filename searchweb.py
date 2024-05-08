import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import logging
from urllib.parse import urlparse
import trafilatura
from urllib.parse import quote
from trafilatura.settings import use_config
from bs4 import BeautifulSoup
from timeout import run_with_timeout
import multiprocessing as mp
import time


logger = logging.getLogger(__name__)

_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

newconfig = use_config()
newconfig.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")


def requests_get(url):
    try:
        response = requests.get(url, headers=_headers, timeout=3, verify=False)
        return response.content
    except Exception as e:
        logger.exception(f'requests_get {str(e)} ... {url}')
        return ''


def get_htmls(links):
    results = []
    try:
        with ThreadPoolExecutor() as executor:
            # 작업 제출 및 Future 객체 저장
            future_to_url = {executor.submit(requests_get, url): url for url in links}
            
            # as_completed 사용하여 완료된 작업 처리
            for future in as_completed(future_to_url, timeout=10):  # 전체 작업에 대한 타임아웃 설정은 없음, 각 작업 처리 시 타임아웃 적용
                url = future_to_url[future]
                try:
                    result = future.result(timeout=10)  # 각 작업에 대해 최대 3초 대기
                    if result:
                        results.append((url, result))
                except Exception as e:
                    print(f"Task failed with exception: {e} for URL: {url}")
                    # 예외 발생 시 결과에서 제외, 따라서 여기서 별도의 처리는 필요 없음
            
        # texts = boosted_requests(links, headers=[_headers] * len(links), timeout=3, max_tries=1, parse_json=False, verbose=False)
    except Exception as e:
        logger.exception(f'get_htmls {str(e)} ... {links}')
        return []
    # texts = list(filter(None, texts))
    return results


def get_content(text, url):
    if text is None:
        if 'namu.wiki' in url:
            return diffbot(url)
        text = requests_get(url)

    if not text.strip():
        return diffbot(url)

    if not text.strip():
        return '', '', ''
    title = ''
    soup = BeautifulSoup(text, "html.parser")
    if soup.title is None:
        title = ''
    else:
        title = soup.title.string

    if not title:
        parsed = urlparse(url)
        title = parsed.netloc
    title = title.strip()

    # thumbnail
    img_src = ''
    og_image = soup.find('meta', property='og:image')
    if og_image and og_image['content']:
        img_src = og_image['content']

    # If the Open Graph tag is not found, search for the first image
    if not img_src:
        first_image = soup.find('img')
        if first_image and first_image['src']:
            img_src = first_image['src']

    # If no image is found, search for the favicon
    if not img_src:
        favicon = soup.find('link', rel='icon')
        if favicon and favicon['href']:
            img_src = favicon['href']

    # title = trafilatura.extract_metadata(text, 'title')
    content = trafilatura.extract(text, config=newconfig)

    # article = Article('http://google.com')
    # article.set_html(text)
    # article.parse()

    # title = article.title
    # content = article.text

    if not content:
        content = ''
    content = content.strip()
    # https://github.com/adbar/trafilatura/issues/202#issuecomment-1140488600 
    return title, img_src, content


def get_content_worker(title, link, content, html):
    try:
        title, img_src, content = run_with_timeout(get_content, 3, html, link)
    except Exception as e:
        parsed = urlparse(link)
        title = parsed.netloc
        title = title.strip()
        img_src = None
        content = ''
    return {'url': link, 'title': title, 'content': content, 'thumbnail': img_src}


def diffbot(url):
    logger.debug(f'diffbot request. {url}')
    url = "https://api.diffbot.com/v3/analyze?token=30eb7c2dabb9f783da7b6f50103beaa0&url=" + quote(url)
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        j = json.loads(response.content)
        title = j['objects'][0].get('title', '')
        image = j['objects'][0].get('images', [{}])[0].get('url', '')
        content = j['objects'][0].get('text', '')

        return title, image, content
    except Exception as e:
        logger.error(url, e)
        return '', '', ''


if __name__ == '__main__':
    # # print(google_serp('프링글스'))
    # d = get_htmls(['https://www.mangoplate.com/search/%EC%84%B8%EA%B3%A1%EB%8F%99'])
    # print(type(d))
    # # with open('test.html', 'w') as w:
    # #     w.write(d[0])
    # print(get_content(d[0]))

    # url test
    # urls = [
    #     'https://newneek.co/post/Fgk56g/',
    #     'https://www.bbc.com/korean/features-64084427',
    #     'https://www.wetax.go.kr/main/?cmd=LPTIOA0R0',
    #     'http://ksetup.com/news/news_view.php?idx_no=10569',
    #     'http://lksdjf.comsdfkljl'
    # ]

    # urls += ['https://ko.hinative.com/questions/2842388', 'https://www.aladin.co.kr/shop/ebook/wPreviewViewer.aspx?itemid=208921735', 'http://css.ulsan.ac.kr/boardCnts/fileDown.do?m=021001&s=css&fileSeq=1056f50b7305b6d541a2ed2454c4455c', 'https://orbi.kr/download/united/11428898/0', 'https://t1.daumcdn.net/cfile/tistory/126BCE464D8980422F?download', 'http://m.blog.naver.com/norunza80/80004911357', 'https://quizlet.com/kr/664421298/%EC%98%81%EC%96%B4%ED%95%99-flash-cards/', 'https://viewpds.jihak.co.kr/tbbf/%EA%B3%A0_Reading%20it_%EC%A0%95%EB%8B%B5%EA%B3%BC%ED%95%B4%EC%84%A4pdf.pdf', 'https://www.jbedu.kr/board/download.jbedu?boardId=BBS_0000024&menuCd=DOM_000000215007003000&startPage=12&dataSid=13749&command=update&fileSid=14972']

    # ds = get_htmls(urls)
    # for d, url in zip(ds, urls):
    #     title, content = get_content(d, url)
    #     if not content:
    #         content = ''
    #     print(title[:50], ' @ ', content[:30].split('\n')[0])

    # import time

    # t = time.time()
    # bing('다다음 소개 -youtube.com')
    # print(time.time() - t)

    print(bing('대한민국 대통령'))
    # bing('대한민국 대통령')

    # print()
