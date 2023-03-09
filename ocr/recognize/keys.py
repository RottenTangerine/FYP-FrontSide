import pickle as pkl

alphabet_list1 = pkl.load(open('ocr/recognize/alphabet.pkl', 'rb'))
alphabet_list2 = pkl.load(open('ocr/recognize/alphabet_hand.pkl', 'rb'))

def add_space(a_list:list):
    if ' ' not in a_list:
        a_list.append(' ')


add_space(alphabet_list1)
add_space(alphabet_list2)

alphabet_list2.sort()
alphabet_list1.sort()

alphabet_machine = [ord(ch) for ch in alphabet_list1]
alphabet_hand = [ord(ch) for ch in alphabet_list2]

