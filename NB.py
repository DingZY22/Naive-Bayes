import re
import os
import math

vocabulary = {}
stop = []
smoothie = 0.5

total_documents = 0
number_of_spam = 0
number_of_ham = 0

def build_model(dir, output, mode):

    global total_documents
    global number_of_spam
    global number_of_ham
    global stop
    files = []

    total_words_ham = 0
    total_words_spam = 0
    size_of_vocabulary = 0
    list = [size_of_vocabulary, total_words_ham, total_words_spam]
    line_counter = 1

    for i in os.listdir(dir):

        if i.startswith('train'):
            if "ham" in i:
                number_of_ham += 1
            elif "spam" in i:
                number_of_spam += 1
            total_documents += 1
            files.append(i)

    if mode == 'stop-words':

        f = open("English-stop-words.txt", "r")
        stop = f.read().split()

    for i in range(total_documents):

        f = open(dir + files[i], "r", encoding='latin-1')
        lower = f.read().lower()
        t = re.split('[^a-zA-Z]', lower)

        if i < number_of_ham:
            for j in range(len(t)):

                if t[j] != "" and stopwords(mode, t[j], stop) is False:
                    list[1] += 1
                    if t[j] not in vocabulary:
                        list[0] += 1
                        vocabulary[t[j]] = [1, 0.0, 0, 0.0]
                    elif t[j] in vocabulary:
                        vocabulary[t[j]][0] += 1

        else:
            for j in range(len(t)):
                if t[j] != "" and stopwords(mode, t[j], stop) is False:
                    list[2] += 1
                    if t[j] not in vocabulary:
                        list[0] += 1
                        vocabulary[t[j]] = [0, 0.0, 1, 0.0]

                    elif t[j] in vocabulary:
                        vocabulary[t[j]][2] += 1

    if mode == 'infrequent-words':

        if ('%' in output):
            indexdot = output.index('.')
            infrequency = int(output[36:indexdot - 1])
            list = mostfrequentwords(infrequency, list)
        else:
            indexdot = output.index('.')
            infrequency = int(output[36:indexdot])
            list = infrequentwords(infrequency, list)


    for key in sorted(vocabulary.keys()):

        vocabulary[key][1] = (vocabulary[key][0] + smoothie) / (list[1] + smoothie * list[0])
        vocabulary[key][3] = (vocabulary[key][2] + smoothie) / (list[2] + smoothie * list[0])

        with open(output, 'a') as the_file:
            the_file.write(str(line_counter) + "  " + key + "  " + str(vocabulary[key][0]) + "  " + str(vocabulary[key][1]) +
                           "  " + str(vocabulary[key][2]) + "  " + str(vocabulary[key][3]) + '\n')
        line_counter += 1


    print("Total words in ham " + str(list[1]))
    print("Total words in spam " + str(list[2]))
    print("Size of vocabulary is " + str(list[0]))


def evaluate_classfier(dir,output):

    files = []
    baseline_classfier = {}
    score_of_spam = 0
    score_of_ham = 0
    line_counter = 1
    totoal_test_documents = 0
    number_right = 0
    global total_documents
    global number_of_spam
    global number_of_ham

    for i in os.listdir(dir):

        if i.startswith('test'):
           files.append(i)
           totoal_test_documents += 1

    for i in range(totoal_test_documents):

        f = open(dir + files[i], "r", encoding='latin-1')

        lo = f.read().lower()
        t = re.split('[^a-zA-Z]', lo)
        baseline_classfier[files[i]] = [0.0, 0.0, '', '', '']

        for j in range(len(t)):
            if t[j] in vocabulary:
                score_of_spam += calculate_score(t[j], 'spam')
                score_of_ham += calculate_score(t[j], 'ham')

        score_of_spam += math.log((number_of_spam / total_documents), 10)
        score_of_ham += math.log((number_of_ham / total_documents), 10)

        baseline_classfier[files[i]][0] = score_of_ham
        baseline_classfier[files[i]][1] = score_of_spam

        if baseline_classfier[files[i]][0] > baseline_classfier[files[i]][1]:
            baseline_classfier[files[i]][2] = 'ham'
        else:
            baseline_classfier[files[i]][2] = 'spam'

        score_of_spam = 0
        score_of_ham = 0

    for key in baseline_classfier:

        if 'spam' in key:
            baseline_classfier[key][3] = 'spam'
        elif 'ham' in key:
            baseline_classfier[key][3] = 'ham'

        if baseline_classfier[key][2] == baseline_classfier[key][3]:
            baseline_classfier[key][4] = 'right'
            number_right += 1;
        else:
            baseline_classfier[key][4] = 'wrong'

        with open(output, 'a') as the_file:
            the_file.write(
                str(line_counter) + "  " + key + "  " + str(baseline_classfier[key][2]) + "  " + str(baseline_classfier[key][0]) +
                "  " + str(baseline_classfier[key][1]) + "  " +
                       str(baseline_classfier[key][3]) + "  " + str(baseline_classfier[key][4]) + '\n')

        line_counter += 1

    print(number_right)
    print((number_right / totoal_test_documents) * 100)


def calculate_score(word,catergories):

    if catergories == 'ham':
        score = math.log(vocabulary[word][1], 10)
    elif catergories == 'spam':
        score = math.log(vocabulary[word][3], 10)

    return score


def stopwords(mode,word,s):

    if mode == 'baseline' or mode == 'infrequent-words' or mode == 'smoothie':
        return False

    elif mode == 'stop-words':

        if word in s:
            return True
        else:
            return False

    elif mode == 'word-length':

        if len(word) <= 2 or len(word) >= 9:
            s.append(word)
            return True
        else:
            return False


def infrequentwords(condition,L):

    deletewords = []
    counter_of_infrequent = 0

    for key in vocabulary:
        words_frequency = vocabulary[key][0] + vocabulary[key][2]
        if words_frequency <= condition:
            counter_of_infrequent += 1
            L[1] -= vocabulary[key][0]
            L[2] -= vocabulary[key][2]

            deletewords.append(key)

    L[0] -= counter_of_infrequent

    for i in range(len(deletewords)):
        del vocabulary[deletewords[i]]

    return L

def mostfrequentwords(condition,L):

    words_to_delete = []
    counter_of_frequent = 0
    topnumber = 0
    vocabulary_frequency = {}

    for key in vocabulary:
        words_frequency = vocabulary[key][0] + vocabulary[key][2]
        if words_frequency not in vocabulary_frequency:
            vocabulary_frequency[words_frequency] = [key]
            counter_of_frequent += 1
        else:

            vocabulary_frequency[words_frequency].append(key)

    topnumber = counter_of_frequent - int(counter_of_frequent * (condition / 100))
    counter_of_frequent = 0

    for key in sorted(vocabulary_frequency.keys()):
        counter_of_frequent+=1
        if(counter_of_frequent >= topnumber):
            for i in range (len(vocabulary_frequency[key])):
                words_to_delete.append(vocabulary_frequency[key][i])

    counter_of_frequent = 0


    for i in range(len(words_to_delete)):

        counter_of_frequent += 1
        L[1] -= vocabulary[words_to_delete[i]][0]
        L[2] -= vocabulary[words_to_delete[i]][2]
        del vocabulary[words_to_delete[i]]
    L[0] -= counter_of_frequent

    return L

if __name__ == '__main__':

    print('Enter a mode:')
    mode = input()

    if mode == '1':

        build_model("Project2-Train/train/", 'model.txt', 'baseline')
        evaluate_classfier("Project2-Test/test/", 'baseline-result.txt')

    elif mode == '2':

        build_model("Project2-Train/train/", 'stopword-model.txt', 'stop-words')
        evaluate_classfier("Project2-Test/test/", 'stopword-result.txt')

    elif mode == '3':

        build_model("Project2-Train/train/", 'wordlength-model.txt', 'word-length')
        evaluate_classfier("Project2-Test/test/", 'wordlength-result.txt')

    elif mode == '4':
        print('Enter the number of removal:')
        infrequency = input()
        outputfile1 = 'infrequentword-model' + infrequency + '.txt'
        outputfile2 = 'infrequentword-result' + infrequency + '.txt'

        build_model("Project2-Train/train/", "Infrequent-Word/" + outputfile1, 'infrequent-words')
        evaluate_classfier("Project2-Test/test/", "Infrequent-Word/" +outputfile2)

    elif mode == '5':


        print('Enter the number of smoothie:')
        user_input = input()
        smoothie =  float(user_input)
        outputfile1 = 'smoothie-model' + user_input + '.txt'
        outputfile2 = 'smoothie-result' + user_input + '.txt'

        build_model("Project2-Train/train/", "Smoothie/" + outputfile1, 'smoothie')
        evaluate_classfier("Project2-Test/test/", "Smoothie/" + outputfile2)





