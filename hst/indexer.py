
class Line(object):
    def __init__(self, txt, seen=0):
        self.txt = txt
        self.seen = 0

class Index(object):
    def __init__(self):
        self.lines = dict()
        self.most_seen = 1
        self.last_lines = []

    def add(self, line):
        if not line:
            return
        existing = self.lines.get(line)
        if existing:
            existing.seen += 1
            if self.most_seen < existing.seen:
                self.most_seen = existing.seen
        else:
            self.lines[line] = Line(line, seen=0)
            self.last_lines.append((0, line))


    def size(self):
        return len(self.lines.keys())

    def find(self, query):
        keywords = query.split(' ')
        results = []
        for k, line in self.lines.iteritems():
            score = 0
            for keyword in keywords:
                if keyword in line.txt:
                    score += 1

            if score > 0:
                # score += difflib.SequenceMatcher(None, query, line.txt).ratio()
                score += line.seen / float(self.most_seen)
                results.append((score, line.txt))

        return results


if __name__ == '__main__':
    i = Index()
    f = file('history.txt')
    fa = f.readlines()
    for l in fa:
        i.add(l)

    print i.size()
    import time
    t1 = time.time()
    i.find('ssh chr.ma')
    print ">>>", time.time() - t1