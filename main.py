from flask import Flask, request, render_template
import requests
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
import dotenv
from findCategoryCode import selectCategoryCode
from Fewshot_Examples.fewshort import getfacet, getvalues

dotenv.load_dotenv()
llm = GoogleGenerativeAI(model="gemini-pro", verbose="True")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

long_tail = ""
category_code = 0
query = ":relevance:"
response = ""
facets = []
value = []
six_digit_numbers = ""
product_elements = []

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        global long_tail, category_code, category_code, query, response, facets, value
        final = []
        long_tail = request.form['long_tail']
        category_code = selectCategoryCode.getcategoryCode(long_tail)
        url = f"https://api.croma.com/searchservices/v1/category/{category_code}?currentPage=0&query={query}&fields=FULL&channel=WEB&channelCode=400049"
        response = requests.get(url).json()["facets"]
        c = 0
        for filtercondition in response:
            if c == 0:
                pass
                c += 1
            else:
                facets.append(filtercondition["code"])
                temp = []
                for j in filtercondition["values"]:
                    facet_value = j["query"]["query"]["value"].split(":")
                    facet_value = facet_value[4] + ":" + facet_value[5]
                    temp.append(facet_value)
                value.append(temp)
        facet_value_pair = list(zip(facets, value))
        print(f"Facets key are {facets}")
        print(f"Facets value are {value}")

        related_facet_key, matched_facet_values = getfacet(long_tail, facets, value)

        for i in matched_facet_values:
            final.append(getvalues(long_tail, i))
        print(final)
        return render_template('search.html', facet_value_pair=facet_value_pair,
                               long_tail=long_tail,
                               related_facet_key=related_facet_key,
                               final=final)
    return render_template('search.html')


@app.route('/results', methods=['POST'])
def results():
    global query
    for key, val in request.form.items():
        if val != "" and key != "long_tail":
            query += str(val).strip() + ":"
    query = query.rstrip(query[-1])
    final_url = f"https://api.croma.com/searchservices/v1/category/{category_code}?currentPage=0&query={query}&fields=FULL&channel=WEB&channelCode=400049"
    print(f"The final request is-{final_url}")
    products = requests.get(final_url).json()["products"]
    return render_template('results.html', long_tail=long_tail,
                           products=products)


if __name__ == '__main__':
    app.run(debug=True, port=9898)
