

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
