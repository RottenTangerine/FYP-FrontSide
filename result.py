

def calculate(stu_answer, answer):
    correct = 0
    total = 0
    stu_ans = stu_answer.split('\n')
    ans = answer.split('\n')
    detail = [[i[1], i[0], i[0] == i[1]] for i in zip(ans, stu_ans)]
    for i in detail:
        if i[2]:
            correct += 1
    total = len(detail)

    return detail, correct, total
