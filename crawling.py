#라이브러리 임포트
#크롤링 : 인터넷에 있는 정보를 긁어옴
import requests  #인터넷 주소(url)에 html 파일을 요청
from bs4 import BeautifulSoup  #그렇게 해서 얻어온 html파일을 예쁘게 '파싱'(필요정보추출)
import pandas as pd
import re  #정규표현식(re),문자열 정제
from io import StringIO

def download_to_csv(df):
    buffer = StringIO()
    df.to_csv(buffer,index=False)
    return buffer.getvalue().encode('utf-8-sig')


#검색어,제외할검색어,지역,경력,학력,페이지 수
#매개변수에 입력될 자료형 '미리안내'
#디폴트 값

#url,header,parameters => requests.get(주소)주소로 요청
#soup객체로 파싱, 가지고 있다가 select(),select_one()으로 필요한파트 추출
#처음에 초기화 해놓은
def crawling_saramin(search_text:str,
                     except_text:str='',
                     region:list = None,
                     category:list =None,
                     career:str='',
                     education:str='',
                     max_pages:int=1):
    #결과로 반환할 데이터 프레임의 '열 이름'과 '행'리스트
    columns = ['이름','위치','조건1','조건2','회사이름','링크']
    rows = []

    #requests로 일단 '검색할 페이지'에 요청
    url = "https://www.saramin.co.kr/zf_user/search"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    }


    #page =>한 페이지 검색결과
    for page in range(1,max_pages+1):
            #파라미터 정제 -> 여기서 파라미터는 '검색 조건'
        #'키'는 웹사이트 지정한 '키'
        parameters = {'searchword':search_text,
                    'except_read':except_text,
                    'comp_page':max_pages}
        #직무
        if category:
            parameters['cat_mcd'] = category
        #위치
        if region:
            parameters['loc_mcd'] = region
        #경력
        if career:
            parameters['career_cd'] = career
        #학력
        if education:
            parameters['edu_cd'] = education

        try:
            response = requests.get(url=url,
                        headers=headers,
                        params=parameters,   #조건에 대한 정보
                        timeout=15)  #html반환해줄때까지 대기시간
            #크롤링 결과를 response로 받고,
            #response안에 있는 text파일을 'html.parser'로 파싱
            #객체 soup를 생성
            soup = BeautifulSoup(response.text,'html.parser')

            #내가 필요한 결과의 '구분자'전달,추출
            #soup.select(구분자): '구분자'를 보유한 모든 내용
            #soup.select_one(구분자): '구분자'를 보유한 내용 딱 하나
            items = soup.select('div.item_recruit')
            for item in items:
                #직무정보(job_area),회사정보(corp_area) 가져옴
                job_area = item.select_one('div.area_job')
                corp_area = item.select_one('div.area_corp')

                #직무정보가 없다!
                if not job_area:
                    #한칸의 정보가 없을 때에는 '이번에만 넘어가자'
                    continue
                #직무,회사정보 get
                job_title = job_area.select_one('.job_tit').get_text(strip=True)
                condition_area = job_area.select_one('.job_condition')

                spans = condition_area.select('span')
                location = spans[0].get_text(strip=True)
                condition1 = spans[1].get_text(strip=True)

                # condition2 = spans[-1].
                job_sector = item.select_one('div.job_sector')
                condition2 = job_sector.get_text(strip=True)

                #회사정보
                cor_name = corp_area.select_one('strong').get_text(strip=True)

                #링크
                link = job_area.select_one('.job_tit').select_one('.data_layer[href]')
                real_link = 'https://www.saramin.co.kr'+link.get('href')

                rows.append({
                    '이름':job_title,
                    '위치':location,
                    '조건1':condition1,
                    '조건2':condition2,
                    '회사이름':cor_name,
                    '링크':real_link
                })
        except Exception as e:
            print(f'에러 발생{e}')
            break

    df = pd.DataFrame(rows)
    #print(df)
    return df

def crawling_work24(search_text:str, 
                     except_text:str = "",
                     region:list = None, 
                     category:list = None,
                     career:str = "",
                     education:str = "",
                     max_pages:int = 1):

    #1.request
    url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do"    
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }
    parameters = {
        'srcKeyword': search_text,
        'notSrcKeyword':  except_text,
        'pageIndex': max_pages,
        'resultCnt': 10,
        'CodeDepth1Info': region,
        'occupation': category,
        'careerTypes': career,
        'academicGbnoEdu': education
    }
    response = requests.get(url,
                            headers=headers,
                            params=parameters,
                            timeout=15)

    #2.soup파싱
    soup = BeautifulSoup(response.text,'html.parser')
    #3.이름,위치,조건1,조건2,회사이름,링크 soup파싱에서 추출
    items1 = soup.select('td.al_left.pd24')
    
    items2 = soup.select('td.link.pd24')

    rows=[]
    for i1,i2 in zip(items1,items2):
        #이름,위치,조건1,조건2,회사이름,링크
        job_title = i1.select_one('.t3_sb.underline_hover').get_text(strip=True)
        link = i1.select_one('.t3_sb.underline_hover[href]')
        cor_name = i1.select_one('.cp_name.underline_hover').get_text(strip=True)  
        #print(link.get("href"))
        real_link = 'https://www.work24.go.kr'+(link.get('href') if link else '')
        
        member = i2.select_one('.member')
        condition_area = member.select('span') if member else []
        career = condition_area[0].get_text(strip=True) if len(condition_area) > 0 else ''
        edu = condition_area[1].get_text(strip=True) if len(condition_area) > 1 else ''
        edu = re.sub(r"\s+", " ", edu).strip()
        location = i2.select_one('.site p').get_text(strip=True)
        salary = i2.select_one('.item.b1_sb').get_text(strip=True) 
        salary = re.sub(r"\s+",' ',salary).strip()
        rows.append({
            '이름':job_title,
            '회사이름':cor_name,
            '위치':location,
            '경력':career,
            '학력':edu,
            '급여':salary,
            '링크':real_link
        })
    
    df = pd.DataFrame(rows)
    #print(df)
    # return '고용24 결과'
    return df 


#진입점
# if __name__ == '__main__':
#     # crawling_saramin("빅데이터")
#     crawling_work24("AI")
