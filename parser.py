import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
    S -> NP VP | S Conj S | S Conj VP

    DT -> Det N | Det AD N
    AD -> Adj | Adj AD
    NP -> N | AD NP | NP PP | DT
    VP -> V | V NP | VP PP | Adv VP | VP Adv
    PP -> P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # split sentence to individual strings and chars in a list
    words = nltk.word_tokenize(sentence)

    # seperate list for lowercases
    lower_words = list()

    # filter in only those contaning at least one alphabet
    for word in words:
        for char in word:
            if char.isalpha():
                lower_words.append(word.lower())
                break

    return lower_words
    # raise NotImplementedError


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # initalize list
    data = []

    # get all the subtrees
    subtrees = tree.subtrees()

    for subtree in subtrees:

        if subtree.label() != 'NP':
            continue
            
        else:
            # check if subtrees contain further 'NP' labels
            sub_subTrees = subtree.subtrees()

            flag = True
            for sub_subTree in sub_subTrees:
                # skip the original subtree
                if sub_subTree is subtree:
                    continue
                if sub_subTree.label() == 'NP':
                    flag = False
                    break
            if flag:
                data.append(sub_subTree)
    return data
    # raise NotImplementedError


if __name__ == "__main__":
    main()
