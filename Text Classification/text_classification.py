import math
import sys

STOPWORDS = set("""
about all along also although among and any anyone anything are around because 
been before being both but came come coming could did each else every for from 
get getting going got gotten had has have having her here hers him his how 
however into its like may most next now only our out particular same she 
should some take taken taking than that the then there these they this those 
throughout too took very was went what when which while who why will with 
without would yes yet you your com doc edu encyclopedia fact facts free home htm html http information 
internet net new news official page pages resource resources pdf site 
sites usa web wikipedia www one ones two three four five six seven eight nine ten tens eleven twelve 
dozen dozens thirteen fourteen fifteen sixteen seventeen eighteen nineteen 
twenty thirty forty fifty sixty seventy eighty ninety hundred hundreds 
thousand thousands million millions
""".split())

def parseInputFile(filename):
    with open(filename, "r") as f:
        lines = [line.strip() for line in f]
    
    # Need to parse the corpus
    i = 0
    corpus = []
    while i < len(lines):
        while i < len(lines) and not lines[i]: # Skipping the empty lines
            i += 1
        if i >= len(lines): # End of file
            break
        # Get the name of person first
        name = lines[i].strip()
        i += 1
        # Line below is the category
        category = lines[i].strip()
        i += 1
        # Line(s) below involves the text
        text = [] 
        while i < len(lines) and lines[i]:
            text.append(lines[i])
            i += 1
        text = " ".join(text)
        corpus.append((name, category, text))
    return corpus


def normalizeText(corpus):
    text = []
    for token in corpus.lower().split():
        token = token.strip(".,")
        if len(token) > 2 and token not in STOPWORDS:
            text.append(token)
    return text


def counting(corpus, num_entries):
    training_corpus = corpus[:num_entries]
    Occ_T_c = {} # Number of biographies of category C in the training corpus
    Occ_T_wc = {} # Number of biographies of category C containing word w in the training corpus

    for _, category, text in training_corpus:
        Occ_T_c[category] = Occ_T_c.get(category, 0) + 1
        words = normalizeText(text)
        for word in words:
            if word not in Occ_T_wc:
                Occ_T_wc[word] = {}
            Occ_T_wc[word][category] = Occ_T_wc[word].get(category, 0) + 1
    
    return Occ_T_c, Occ_T_wc


def calculateProbabilities(Occ_T_c, Occ_T_wc):
    categories = list(Occ_T_c.keys())
    T = sum(Occ_T_c.values()) # Total number of biographies in the training corpus
    epsilon = 0.1 # Smoothing parameter
    Prob_C = {}
    for cat in categories:
        frequency_cat = Occ_T_c[cat]/T # Fraction of biographies of category C in the training corpus
        Prob_C[cat] = (frequency_cat + epsilon) / (1 + len(categories) * epsilon) # Calculated using Laplacian correction
    Prob_W_C = {}
    for word, category_count in Occ_T_wc.items():
        Prob_W_C[word] = {}
        for cat in categories:
            frequency_wc = category_count.get(cat, 0) / Occ_T_c[cat]
            Prob_W_C[word][cat] = (frequency_wc + epsilon) / (1 + 2 * epsilon)
    return Prob_C, Prob_W_C


def classify(corpus, num_entries, Prob_C, Prob_W_C):
    output_file = "output.txt"
    with open(output_file, "w") as f:
        test_corpus = corpus[num_entries:]
        categories = list(Prob_C.keys())
        correct_cat_count = 0
        for name, category, text in test_corpus:
            words = normalizeText(text)
            L = {}
            for c in categories:
                Lc = -math.log(Prob_C[c], 2) # Computing negative log probabilities to avoid underflow
                sum_words = 0.0
                for word in words:
                    if word in Prob_W_C:
                        sum_words += -math.log(Prob_W_C[word].get(c, 0.1/(1 + 2 * 0.1)), 2)
                L[c] = Lc + sum_words
            
            # Find the minimum
            m = min(L.values()) # 4a
            xs = {}
            for c, lc in L.items():
                xs[c] = 2**(m - lc) if (lc - m) < 7 else 0.0 # 4b
            sum_xs = sum(xs.values())
            posterior_probs = {c: (xs[c] / sum_xs if sum_xs > 0 else 0.0) for c in categories} # 4c
            predict = max(posterior_probs, key=posterior_probs.get)
            if predict == category:
                correct_cat_count += 1
            f.write(f"{name}. Prediction: {predict}. {'Right' if predict == category else 'Wrong'}.")
            f.write("\n")
            for c in categories:
                f.write(f"{c}: {posterior_probs[c]:.2f}   ")
            f.write("\n")
            f.write("\n")
        f.write(f"Overall accuracy: {correct_cat_count} out of {len(test_corpus)} = {correct_cat_count/len(test_corpus):.2f}.")
        f.close()


def main():
    corpus_file = sys.argv[1]   
    num_entries = int(sys.argv[2])
    corpus = parseInputFile(corpus_file)
    
    Occ_T_c, Occ_T_wc = counting(corpus, num_entries)
    Prob_C, Prob_W_C = calculateProbabilities(Occ_T_c, Occ_T_wc)
    classify(corpus, num_entries, Prob_C, Prob_W_C)


if __name__ == "__main__":
    main()