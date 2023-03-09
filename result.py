def calculate(stu_answer:str, answer:str):
    stu_answer = stu_answer.replace('\r', '')
    answer = answer.replace('\r', '')

    stu_ans = stu_answer.split('\n')
    ans = answer.split('\n')
    print(stu_answer, answer)

    detail = [[i[1], i[0]] for i in zip(ans, stu_ans)]
    result_list = [i[0] == i[1] for i in detail]
    correct = sum(result_list)
    total = len(detail)

    return detail, result_list, correct, total
