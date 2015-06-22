

def subsequenceMatch(uctext, ucterm):
    """
    #returns array of the indices in uctext where the letters of ucterm were found.
    # EG: subsequenceMatch("nothing", "ni") returns [0, 4]. subsequenceMatch("nothing", "a")
    # returns null.
	#simple subsequence match
	"""
    hits = []
    texti = -1
    termi = 0
    while termi < len(ucterm):
        texti = uctext.find(ucterm[termi], texti + 1) #search for character & update position
        if texti == -1:  #if it's not found, this term doesn't match the text
            return None
        hits.append(texti)
        termi += 1
    return hits

#
def skipMatch(uctext, ucterm, acry):
    #subsequence match that tries to match the letters at the beginnings of the words (IE, after a space, an underscore, or camelcase hump) instead of the first letters it finds when it can. Those words are specified in acry (short for acronym), which is an array of the indexes of the word beginnings in uctext.
    #returns the same kind of hits array as subsequenceMatch

    #possible methods to explore once performance testing: try having it branch every time it faces a choice between skipping ahead to match an initial and continuing with a greedy substring match, get better results.

    hits = []
    ai = 0
    texti = -1
    termi = 0
    while termi < len(ucterm):
        char = ucterm[termi]
        #see if we can match a word beginning
        ait = ai
        while ait < len(acry):
            if char == uctext[acry[ait]]:
                break
            ait += 1
        if ait < len(acry): #we can match a word beginning. leap there
            texti = acry[ait]
            ai = ait + 1
        else:
            #normal subsequence matching
            texti = uctext.find(ucterm[termi], texti + 1) #search for character & update position
            #ensure that the ai stays ahead of the texti, or else invalidate it
            while ai < len(acry) and texti > acry[ai]:
                ai += 1
            if texti == -1:  #if it's not found, this term doesn't match the text
                return None
        hits.append(texti)
        termi += 1
    return hits

#
#
def matching(candidate, term, hitTag):
    #this method tries skipMatch, then subsequenceMatch if there is no skipMatch. It then scores the result.
    #if no match, returns null, else {score, matched:<text with match tags inserted>}
    text = candidate['text']
    acry = candidate['acronym']
    uctext = text.upper()
    ucterm = term.upper()
    outp = {'score':1}

    hits = skipMatch(uctext, ucterm, acry) or subsequenceMatch(uctext, ucterm)
    if not hits:
        return None

    def find(a, search, start):
        for i in range(start, len(a)):
            if a[i] == search:
                return i
        return -1

    #post hoc scoring
    #points for matches at word beginnings
    ji = -1
    for hit in hits:
        ji = find(acry, hit, ji+1)
        if ji >= 0:
            if ji == 0:
                n = 48
            else:
                n = 30
            outp['score'] += n

    #points for matching the case
    for i in range(0, len(hits)):
        if term[i] == text[hits[i]]:
            outp['score'] += 11
    ai = 0
    #prefers longer words as short ones rarely need autocompletion
    if len(text) > 4:
        outp['score'] += 20

    if hitTag:
        #produce search result with match tags
        i = 0
        splittedText = []
        lastSplit = 0
        #divide the string at the insertion points
        while i < len(hits):
            #find the end of this contiguous sequence of hits
            ie = i
            while True:
                ie += 1
                if ie >= len(hits) or hits[ie] != hits[ie - 1] + 1:
                    break
            #points are scored for contiguous hits
            outp['score'] += (ie - i - 1)*18
            tagstart = hits[i]
            tagend = hits[ie - 1] + 1
            splittedText.append(text[lastSplit:tagstart])
            lastSplit = tagstart
            splittedText.append(text[lastSplit:tagend])
            lastSplit = tagend
            i = ie
        cap = text[lastSplit:]
        #join that stuff up
        i = 0
        cumulation = ''
        startTag = '<span class="'+hitTag+'">'
        endTag = '</span>'
        while i < len(splittedText):
            cumulation += splittedText[i] + startTag + splittedText[i + 1] + endTag
            i += 2
            outp['matched'] = cumulation + cap
    else:
        #otherwise just add the contiguosity points
        for i in range(1, len(hits)):
            if hits[i - 1] + 1 == hits[i]:
                outp['score'] += 18
    return outp

# isLowercase = (charcode)-> (charcode >= 97 and charcode <= 122)
# isUppercase = (charcode)-> (charcode >= 65 and charcode <= 90)
# isNumeric = (charcode)-> (charcode >= 48 and charcode <= 57)
#
# isAlphanum = (charcode)-> (isLowercase charcode) or (isUppercase charcode) or (isNumeric charcode)
#

def isAlphanum(char):
    return char.isupper() or char.islower() or char.isdigit()

class MatchSet(object):
    def __init__(self, termArray, hitTag, matchAllForNothing):
        self.hitTag = hitTag
        self.matchAllForNothing = matchAllForNothing
        self.takeSet(termArray)

    def takeSet(self, termArray): #allows [[text, key]*] or [text*], in the latter case a text's index in the input array will be its key
        #does not currently maintain an index..
        #shunt termArray into the correct form
        self.set = []
        if termArray:
            if isinstance(termArray[0], str):
                self.set = [(st, i) for i, st in enumerate(termArray)]
            else:
                self.set = termArray
        ret = []
        for text, key in self.set:
            ar = []
            if text:
                for j in range(0, len(text)):
                    char = text[j]
                    if (
                            (char.isupper()) or
                            isAlphanum(char) and
                            (j == 0 or not isAlphanum(text[j - 1])) #not letter
						):
                        ar.append(j)

            ret.append({'text': text,
		    'key': key,
		    'acronym': ar})
        self.set = ret
        #@set is like [{acronym, text, key}*] where acronym is an array of the indeces of the beginnings of the words in the text

    def seek(self, searchTerm, nresults = 10): #returns like [{score, matched:<the text with match spans inserted where a letter matched>, text, key}*]
        #we sort of assume nresults is going to be small enough that an array is the most performant data structure for collating search results.
        if (not self.set) or nresults == 0:
            return []

        if not searchTerm:
            if self.matchAllForNothing:
                ret = []
                for sel in self.set:
                    ret.append({
						'score': 1, #shrug
						'matched': sel.text,
						'text': sel.text,
						'key': sel.key,
					})
                return ret
            else:
                return []
        retar = []
        minscore = 0
        # return self.set
        for c in self.set:
            sr = matching(c, searchTerm, self.hitTag)
            if sr and (sr['score'] > minscore or len(retar) < nresults):
                insertat = 0
                for insertat in range(0, len(retar)):
                    if retar[insertat]['score'] < sr['score']:
                        break
                sr['key'] = c['key']
                sr['text'] = c['text']
                retar = splice(retar, sr, insertat, 0)
                if len(retar) > nresults:
                    retar.pop()
                minscore = retar[:-1]
        return retar


    def seekBestKey(self, term):
        res = self.seek(term, 1)
        if len(res) > 0:
            return res[0].key
        else:
            return None

def splice(s, replace, start, end):
    return s[:start] + [replace] + s[end:]

#
def matchset(ar, hitTag='subsequence_match', matchAllForNothing=False):
    return MatchSet(ar, hitTag, matchAllForNothing)

if __name__ == '__main__':
    ms = matchset([
      ['Binding Lantern Smith', 0],
      ['Hopeful Woods', 1],
      ['blustery_green', 2],
      ['Holy Sword', 3]
    ])
    print "--------------------"
    print ms.seek('bl')