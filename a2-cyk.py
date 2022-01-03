#!/usr/bin/env python
# coding: utf-8

# In[1]:


#260917834 Haochen LIU COMP550A2Q2
from nltk import CFG
from nltk.tree import *


# In[105]:


class Node:
    
    def __init__(self, tag, lChild,rChild=None,parent = None):
        self.tag = tag
        self.lChild = lChild
        self.rChild = rChild
        self.parent = parent
    def __getTag__(self):
        return self.tag
    
    def __repr__(self):
        if self.rChild == None and self.parent == None:
            return self.tag+" "+"->"+" "+self.lChild #+" "+"parent"+self.parent
        if not(self.rChild == None) and self.parent == None:  
            return self.tag+" "+"->"+" "+self.lChild+" "+self.rChild #+" "+"parent"+self.parent
        if self.rChild == None and not(self.parent == None):
            return self.tag+" "+"->"+" "+self.lChild+" "+"parent"+" "+self.parent.tag
        return self.tag+" "+"->"+" "+self.lChild+" "+self.rChild+" "+"parent"+" "+self.parent.tag


# In[156]:


# helper functions for CYK class
def getWordTags(word,rules):
    result = []
    for i in range(len(rules)):
        for j in range(len(rules[i])-2):
            if rules[i][j+2] == "'"+ word +"'":
                result.append(rules[i][0])
    
    return result

def getRules(lChild,rChild,rules):
    result = []
    rulesToCheck = []
    for i in range(len(lChild)):
        for j in range(len(rChild)):
            rulesToCheck.append([lChild[i],rChild[j]])
    
    
    for rule in rules:
        for toCheck in rulesToCheck:
            if len(rule)>3 and rule[2]==toCheck[0] and rule[3] == toCheck[1]:
                result.append(rule)
    return result

def CheckExistInBasicGrammar(tagToCheck, basicGrammar):
    for rule in basicGrammar:
        if rule[0] == tagToCheck:
            return true
    return false

# if table is correctly filled, will return a syntatic tree,
# but it is not according to the original rules but the rules in
# CNF form
def GenerateTree(row, column, tagToCheck, table, basicGrammar):
    cell = table[row][column]
    if cell != []:
        for i in range(len(cell)):
            if cell[i].tag == tagToCheck:
                print(tagToCheck)
                node = cell[i]
                if node.lChild[0]=="'":
                    return Tree(node.tag, [node.lChild])
                else:
                    
                    lTagToFind = node.lChild
                    rTagToFind = node.rChild
                    #确定lchind位置
                    lChildPos = (0,0)
                    for c in range(0,column):
                        if table[row][c]!=[]:
                            for node_2 in table[row][c]:
                                if node_2.tag == lTagToFind:
                                    lChildPos = (row,c)
                    #确定rchild位置
                    rChildPos = (lChildPos[1],column)
                    return Tree(node.tag, [GenerateTree(lChildPos[0],lChildPos[1],node.lChild,table,basicGrammar), 
                                           GenerateTree(rChildPos[0],rChildPos[1],node.rChild,table,basicGrammar)])


# In[197]:


class CYK:
    
    def __init__(self,cfg_grammar):
        self.raw = cfg_grammar
        
        r = str(cfg_grammar)
        r=r.split("\n")
        for i in range(len(r)):
            r[i] = r[i].split()
        self.basic = r[1:]
        self.cfg = None
    # with flaw, not working properly
    def CFGtoCNF(self):
        # preprocessing input
        rules_list = self.basic
        # split up the string

        # rule list now finished preprocesses  

        # eliminate mix of terminal and non-terminal on rhs
        # eliminate rhs with >2 terminals
        for rule in rules_list:
            # only one terminal/nonterminal on rhs
            if len(rule) == 3:
                continue
            # now the rule must have more 1 terminal/nonterminal
            # check whether rhs contains terminal
            else:
                terminal_check = False
                terminal_index = []
                for i in range(len(rule)):
                    if rule[i][0]=="'":
                        new_nonT = rule[i][1:].upper()
                        new_nonT = new_nonT[:-1]
                        rules_list.append([new_nonT,'->',rule[i]])
                        rule[i]=new_nonT

                while len(rule)>=5:
                    new_nonT = rule[2]+"_"+rule[3]
                    rules_list.append([new_nonT,'->',rule[2],rule[3]])                
                    rule[2]=new_nonT
                    rule.pop(3)

        # remove useless ones that are unable to terminate
        for rule in rules_list:
            lhs = rule[0]
            if rule[-1]==rule[0]:
                rules_list.remove(rule)

        # remove useless that never appear in rhs
        for rule in rules_list:
            toCheck = rule[0]
            useless = True;
            for rules2 in rules_list:
                if toCheck in rules2[2:]:
                    useless = False
                    break
            if useless and rule[0]!='S':
                print(rule)
                rules_list.remove(rule)
                continue         

        # remove unit production
        for i in range(len(rules_list)):
            rule = rules_list[i]
            if len(rule)==3 and rule[2][0]!="''":
                for rule_2 in rules_list:
                    if rule_2[0]==rule[2]:
                        new_rule = rule[0:1]+rule_2[1:]
                        rules_list[i]=new_rule

        print("------------------------------------")
        self.cfg = rules_list
        return rules_list



    # works properly when rules are already in proper CNF form
    # because the implementation of CFGtoCNF has flaws
    # there is a example from class shown below
    def FillTable(self, sentence):
        rules = self.CFGtoCNF()
        words = sentence.split()
        size = len(words)
        table = [[[] for i in range(size+1)] for j in range(size+1)]

        for i in range(size):
            word = words[i]
            tag = getWordTags(word,rules)
            for j in range(len(tag)):
                table[i][i+1].append(Node(tag[j],"'"+word+"'"))

        # size-1
        for i in range(1,size):
            # size - i
            for j in range(i,size):
                row= j-i
                column = j+1
                out = str(row)+":"+str(column)
                for k in range(row+1,column):
                    lCell = table[row][k]
                    rCell = table[k][column]
                    lTag = []
                    rTag = []
                    for m in range(len(lCell)):
                        lTag.append(lCell[m].tag)
                    for m in range(len(rCell)):
                        rTag.append(rCell[m].tag)
                    if lTag != [] and rTag != []:
                        relatedRules = getRules(lTag,rTag,rules)
                        for m in range(len(relatedRules)):
                            toAdd = relatedRules[m]
                            nodeUpper = Node(toAdd[0],toAdd[2],toAdd[3])
                            table[row][column].append(nodeUpper)
                            for node in lCell:
                                if node.tag == toAdd[2]:
                                    node.parent = nodeUpper
                            for node in rCell:
                                if node.tag == toAdd[3]:
                                    node.parent = nodeUpper

        return table
    
    def parse(self, sentence):
        table = self.FillTable(sentence)
        size = len(sentence.split(" "))
        tree = GenerateTree(0, 7,"S",table,self.basic)
        tree.pretty_print()


# In[199]:


# doesn't work good for raw grammar rules
# table filling is problematic
cfg3 = CFG.fromstring("""
S -> NP VP
VP -> V NP PP | V NP
NP -> N | Det N | Det N PP
PP -> 'in' NP
N -> 'I' | 'elephant' | 'pyjamas'
V -> 'shot'
Det -> 'my' | 'the'
""")
test = CYK(cfg3)
test.CFGtoCNF()
test.FillTable("I shot the elephant in my pyjamas")
#test.parse("I shot the elephant in my pyjamas")


# In[200]:


# but when using correct CNF format rules,
# the table can be filled and a tree(but not in raw grammar)
# can be generated
sample = CFG.fromstring("""S -> NP VP
VP -> X1 PP
VP -> V NP
NP -> Det N
NP -> X2 PP
PP -> P NP
P -> 'in'
NP -> 'I' | 'elephant' | 'pyjamas'
N -> 'I' | 'elephant' | 'pyjamas'
V -> 'shot'
Det -> 'my' | 'the'
X1 -> V NP
X2 -> Det N
""")
test = CYK(sample)
test.CFGtoCNF()
test.parse("I shot the elephant in my pyjamas")

