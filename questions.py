import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    os.chdir(os.path.join(os.getcwd(), directory))

    data = dict()

    for file in os.listdir():

        if ".txt" not in file:
            continue

        # encoding is necessary in order to retrieve data
        with open(file, encoding="utf8") as f:
            data[file] = f.read()

    old_dir = os.path.split(os.getcwd())

    # go back to original directory
    os.chdir(old_dir[0])

    return data
    # raise NotImplementedError


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # create list from string(all lowercase)
    tokenized = nltk.word_tokenize(document.lower())

    filtered = list()

    for word in tokenized:

        # check if word is a punctuation
        if word in string.punctuation:
            continue

        # check if a word is an ordinary grammar word
        if word in nltk.corpus.stopwords.words('english'):
            continue

        filtered.append(word)

    return filtered
    # raise NotImplementedError


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # total number of documents
    total_docs = len(documents.keys())

    # calculate occurances of word in number of documents
    word_doc = dict()

    for doc, lis in documents.items():

        # typecast to set to avoid repition of words
        no_repeat = set(lis)

        for word in no_repeat:

            # initialize
            if word_doc.get(word, None) is None:
                word_doc[word] = 1

            else:
                word_doc[word] += 1

    idf_data = dict()

    # idf(word) = log(total num of docs / no of docs having that word)
    for word, freq in word_doc.items():
        idf_data[word] = math.log(total_docs / freq)

    return idf_data
    # raise NotImplementedError


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    tf_idf_data = dict()

    for word in query:
        for file, words in files.items():

            # calculate frequency of word in file
            count = 0
            for w in words:
                if word == w:
                    count += 1

            # tf-idf(file) = frequency of word in file * idf(word)
            if tf_idf_data.get(file, None) is None:
                tf_idf_data[file] = count * idfs[word]
            else:
                tf_idf_data[file] += count * idfs[word]

    # sorting according to tf-idf(higest first)
    sorted_data = sorted(tf_idf_data.items(),
                         key=lambda x: x[1], reverse=True)

    ranked_files = [x for x, _ in sorted_data]

    n_files = list()
    for x in range(len(ranked_files)):
        if x >= n:
            break
        n_files.append(ranked_files[x])

    return n_files
    # raise NotImplementedError


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # maps sentence to list[idf, query-term-density]
    data = dict()
    for word in query:
        for sentence, words in sentences.items():

            # initialize if not present already
            if data.get(sentence, None) is None:
                data[sentence] = [0, 0]

            # calculate frequency of word in sentence
            count = 0
            for w in words:
                if word == w:
                    # first priority -> idf(word)
                    data[sentence][0] += idfs[word]
                    count += 1

            # second priority -> query term density
            data[sentence][1] += count / len(words)

    # sort as per idf(word) and if clash then (query term density)
    sorted_data = sorted(data.items(),
                         key=lambda x: x[1], reverse=True)

    ranked_sentences = [x for x, _ in sorted_data]

    n_sentences = list()
    for x in range(len(ranked_sentences)):
        if x >= n:
            break
        n_sentences.append(ranked_sentences[x])
    return n_sentences
    # raise NotImplementedError


if __name__ == "__main__":
    main()
