

def calculate(text, answer):
    correct = 0
    total = 0
    txt = text.split('\r\n')
    ans = answer.split('\n')
    detail = [[i[0], i[1], i[0] == i[1]] for i in zip(txt, ans)]
    for i in detail:
        if i[2]: correct += 1
    total = len(detail)

    return detail, correct, total



if __name__ == '__main__':
    _answer = """a
c
b
b
d
468000
万里长城
Machine Learning
20cm"""

    _text = """b
c
a
b
d
468000
岳阳楼
Machine Learning
20m"""

    _detail, _correct, _total = calculate(_text, _answer)
    print(_detail, _correct, _total)
