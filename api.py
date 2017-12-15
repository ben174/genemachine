from flask import Flask, jsonify


class GeneDB(object):
    def __init__(self):
        self.labels = []
        self.fields = []
        self.genes = {}
        self.friendly_names = {}
        self.keys = []

    def read_data(self):
        with open('variant_results.tsv', 'r') as f:
            headers = f.readline().rstrip()
            self.labels = headers.split('\t')
            self.fields = headers.lower().replace(' ', '_').split('\t')
            self.friendly_names = dict(zip(self.fields, self.labels))
            for line in f:
                try:
                    values = line.rstrip().split('\t')
                except UnicodeDecodeError as e:
                    print 'Error decoding line: {}'.format(str(e))
                record = dict(zip(self.fields, values))
                self.genes[record['gene']] = record
        self.keys = sorted([w.upper() for w in self.genes.keys()])

    def get_matches(self, query):
        return [m for m in self.keys if m.startswith(query.upper())]


# initialize gene database, and load data from TSV
genedb = GeneDB()
genedb.read_data()

# initialize API
app = Flask(__name__)


@app.route('/api/v1/suggest/<query>/', methods=['GET'])
def suggest(query):
    matches = genedb.get_matches(query)
    response = jsonify(matches)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/v1/retrieve/<query>/', methods=['GET'])
def retrieve(query):
    matches = genedb.get_matches(query)
    records = [genedb.genes[m] for m in matches]
    return jsonify(records)


@app.route('/api/v1/genes/', methods=['GET'])
def all_genes():
    return jsonify(genedb.genes)


@app.route('/api/v1/keys/', methods=['GET'])
def all_keys():
    response = jsonify(genedb.keys)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
