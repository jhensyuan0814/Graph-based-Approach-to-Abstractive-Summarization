import nltk
import math
import sys
from operator import eq 
import argparse

def OpinosisGraph(Z, G, PRI):  #paper Alg1
    for i in range(len(Z)):  
        for j in range(len(Z[i])):  
            LABEL = Z[i][j]
            PID = j
            SID = i
            if LABEL in G:
                PRI[LABEL].append((SID, PID))
            else:
                G[LABEL] = list()
                PRI[LABEL] = [(SID, PID)]
            if j > 0 and LABEL not in G[Z[i][j-1]]:
                G[Z[i][j-1]].append(Z[i][j])
                
def VSN(node):   #paper def 1
    global PRI1
    sigma_vsn = 15
    ele = PRI1[node]
    sum = 0
    for i in range(len(ele)):
        sum = sum + ele[i][1]
    return (sum/len(ele)) <= sigma_vsn

def collapsible(node):  #paper def 5
    if(node[1] == 'VERB'):
        return True
    else: 
        return False

def valid_sent(sent):     #paper doesn't specify how to find a valid sentence in grammar
    return True

def check_inter(PRIa,PRIb):  #paper Alg3 line12
    PRIc = []
    sigma_gap = 4
    for first in PRIa:
        for second in PRIb:
            if(first[0] == second[0] and abs(first[1]-second[1]) <= sigma_gap):
                PRIc.append(second)
    return PRIc

def common_elements(list1, list2):  #paper Alg3 line22
    count = 0
    for element in list1:
        if element in list2:
            count= count+1
    return count
                                            
def jaccard_fail(a,b):   #paper Alg2 line14: eliminate duplicates with jaccard similarity
    sigma_j = 0.3
    inter = common_elements(a,b)
    return ((inter/(len(a)+len(b)-inter)) >= sigma_j)
    

def eliminate_dup(clist): #paper Alg2 line14: eliminate duplicates with jaccard similarity
    buf = []
    first = True
    for ele in clist:
        temp = []
        similar = False
        if(first):
            buf.append(ele)
            first = False
        else:
            for seen in buf:
                if jaccard_fail(seen[0],ele[0]):
                    similar = True
                    if ele[1]>seen[1]:                           
                        temp.append(seen)
            if len(temp) != 0:  
                for seen in temp:
                    buf.remove(seen)
                buf.append(ele)
            elif similar == False:
                buf.append(ele)  
    return buf



def find_avg_score(clist):    #paper Alg3 line23
    if len(clist)==0:
        return 0
    sum = 0
    for ele in clist:
        sum = sum + ele[1]
    return sum/len(clist)

def find_sum(C):             #paper Alg2 line16,17
    winner = (None,-1)
    runner_up = (None,-1)
    for ele in C:
        if ele[1] > winner[1]:
            if winner[1] > runner_up[1]:
                runner_up = winner
            winner = ele
        elif ele[1] > runner_up[1]:
            runner_up = ele
    ans1 = ""
    for words in winner[0]:
        ans1 = ans1 + words[0] + " "
    ans1 = ans1[0].upper() + ans1[1:(len(ans1)-1)]
    ans2 = ""
    for words in runner_up[0]:
        ans2 = ans2 + words[0] + " "
    ans2 = ans2[0].upper() + ans2[1:(len(ans2)-1)]
    return ans1,ans2

def Traverse(clist,vk,score,PRI_overlap,sent,length, original_sentence):    #paper Alg3
    #print(sent)
    global G1
    global PRI1
    global sentence_number
    global neighbor
    sigma_r = 0
    redundancy = len(PRI_overlap)
    if length>100:        #we add a path length limit here, so the program won't have recursion error
        return
    if (redundancy / length >= sigma_r):  
        if (neighbor == len(original_sentence[sentence_number])):
            if (valid_sent(sent)):
                finalscore = score/length
                clist.append((sent,finalscore))
                return 
        else:
            vn = original_sentence[sentence_number][neighbor]
            neighbor += 1
            PRI_new = check_inter(PRI_overlap,PRI1[vn])
            redundancy = len(PRI_new)
            new_sent = sent+[vn]
            L = length + 1
            new_score = score + redundancy  
            Traverse(clist,vn,new_score,PRI_new,new_sent,L, original_sentence)
    
def first_lower(s):     #string processing
    return s.lower()
        
def read_text(file_name):    #readfile
    redundant = '<br />'
    review = []
    with open(file_name,'r') as file:
        for article in file:
            article = article.replace(redundant," ")
            sentences = nltk.sent_tokenize(article) 
            for sentence in sentences:
                sentence = first_lower(sentence)
                review.append(nltk.pos_tag(nltk.word_tokenize(sentence),tagset='universal'))           
    file.close()
    return review

def main():
    global G1
    global PRI1
    global sentence_number
    global neighbor
    filenames = [sys.argv[1]]
    for name in filenames:
        a,b = name.split('.')
        original_sentence = []
        if b == 'txt':
            print(name)
            Z1 = read_text(name)
            Z2 = []
            for i in Z1:
                original_sentence.append(i)
                Z2.append(i[0])
            G1 = dict()
            PRI1 = dict()
            OpinosisGraph(Z1, G1, PRI1)   #paper Alg2
            candidates = []
            for i in range(len(Z2)):
                keys = Z2[i]
                sentence_number = i
                neighbor = 1
                if(VSN(keys)):
                    clist = []
                    sum_sent = [keys]
                    score = 0
                    Traverse(clist,keys,score,PRI1[keys],sum_sent,1, original_sentence)
                    candidates = candidates + clist
            C = eliminate_dup(candidates)
            summary = find_sum(C)
            print("summary1: ",summary[0])
            if len(sys.argv) == 2 or sys.argv[2] == '2':
                print("summary2: ",summary[1])
if __name__ == '__main__':
    print("python extractive_version.py input_file number_of_summary(1 or 2)")
    main()