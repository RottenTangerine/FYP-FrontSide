import pickle as pkl

alphabet_list1 = pkl.load(open('alphabet.pkl', 'rb'))
alphabet_list2 = pkl.load(open('alphabet2.pkl', 'rb'))

alphabet_list = list(set(alphabet_list1 + alphabet_list2))
alphabet_list.sort()

alphabet = [ord(ch) for ch in alphabet_list]
alphabet_v2 = alphabet
