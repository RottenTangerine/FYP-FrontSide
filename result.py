def calculate(stu_answer, answer):
    stu_ans = stu_answer.split('\r\n')
    # print(stu_ans)
    ans = answer.split('\r\n')
    # print(ans)
    detail = [[i[1], i[0]] for i in zip(ans, stu_ans)]
    result_list = [i[0] == i[1] for i in detail]
    correct = sum(result_list)
    total = len(detail)

    return detail, result_list, correct, total
