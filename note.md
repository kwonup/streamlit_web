# 크롤링 학습 메모

## 오늘 작성한 코드 흐름

- `requests.get()`으로 채용 사이트 HTML을 요청한다.
- `response.text`로 응답 객체 안의 HTML 문자열을 꺼낸다.
- `BeautifulSoup(response.text, "html.parser")`로 HTML을 파싱한다.
- `select()`는 조건에 맞는 요소 여러 개를 리스트로 가져온다.
- `select_one()`은 조건에 맞는 요소 하나만 가져온다.
- 공고 목록을 반복문으로 돌면서 제목, 회사명, 위치, 조건, 링크를 추출한다.
- 추출한 데이터는 딕셔너리로 만들고 `rows.append()`로 리스트에 모은다.
- 마지막에 `pd.DataFrame(rows)`로 표 형태로 바꿔 출력한다.

## 헷갈렸던 부분

- `response`는 응답 객체이고, 실제 HTML 내용은 `response.text`에 있다.
- `get_text(strip=True)`에서 `strip`을 `stirp`로 잘못 쓰면 에러가 난다.
- `select_one()`이 요소를 못 찾으면 `None`이 나오므로 바로 `.get_text()`를 붙이면 `NoneType` 에러가 날 수 있다.
- 함수가 인자를 받지 않게 정의되어 있는데 `crawling_work24("AI")`처럼 값을 넘기면 `takes 0 positional arguments but 1 was given` 에러가 난다.
- `requests.get(..., params=parameters)`에 넣는 `parameters`는 `{key: value}` 형태의 딕셔너리여야 한다.
- `rows.append()`를 정보 종류별로 따로 하면 한 공고가 여러 딕셔너리로 쪼개진다. 같은 공고의 정보는 한 딕셔너리에 모아서 한 번만 append해야 한다.
- Work24에서 회사명 링크는 `href="#none"`이라 실제 공고 링크가 아니었다. 공고 제목 링크인 `.t3_sb.underline_hover[href]`를 사용해야 한다.

## 공백 정리

- `replace(" ", "")`는 모든 띄어쓰기를 없애서 의미 있는 공백까지 사라질 수 있다.
- 줄바꿈, 탭, 여러 칸 공백을 정리할 때는 정규표현식이 더 좋다.

```python
condition2 = condition_area[1].get_text(strip=True)
condition2 = re.sub(r"\s+", " ", condition2).strip()
```

이렇게 하면 `\r\n`, `\t`, 여러 칸 공백이 공백 하나로 정리된다.

## 정규표현식 간단 정리

- 정규표현식은 문자열에서 특정 패턴을 찾거나 바꿀 때 쓰는 문법이다.
- 파이썬에서는 `re` 모듈을 사용한다.
- `re.sub(패턴, 바꿀문자, 대상문자열)`은 패턴에 맞는 부분을 찾아 다른 문자로 바꾼다.

```python
import re

text = "대졸(2~3년)\r\n\t\t ~ 대졸(4년)"
text = re.sub(r"\s+", " ", text).strip()
```

- `r"..."`는 raw string이라서 `\s` 같은 정규표현식 문자를 편하게 쓸 수 있다.
- `\s`는 공백 문자 전체를 뜻한다. 띄어쓰기, 줄바꿈(`\n`), 탭(`\t`) 등이 포함된다.
- `+`는 앞의 패턴이 하나 이상 반복된다는 뜻이다.
- 그래서 `r"\s+"`는 "공백이 한 개 이상 이어진 부분"을 의미한다.

## 기억할 패턴

```python
tag = item.select_one(".some_class")
text = tag.get_text(strip=True) if tag else ""
```

요소가 없을 수도 있는 크롤링 코드에서는 이렇게 안전하게 가져오는 습관이 좋다.
