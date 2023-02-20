import pickle as pkl

alphabet_list1 = pkl.load(open('ocr/recognize/alphabet.pkl', 'rb'))
alphabet_list2 = pkl.load(open('ocr/recognize/alphabet2.pkl', 'rb'))

alphabet_list2.sort()
alphabet_list1.sort()

alphabet = [ord(ch) for ch in alphabet_list1]
alphabet_v2 = [ord(ch) for ch in alphabet_list2]
