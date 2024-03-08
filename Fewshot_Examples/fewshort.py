import json
import dotenv
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.prompts.example_selector import (MaxMarginalRelevanceExampleSelector)
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain_openai import OpenAI

dotenv.load_dotenv()
llm = GoogleGenerativeAI(model="gemini-1.0-pro", verbose="True")


# llm = OpenAI(verbose="True")


def getfacet(long_tail, facets, values):
    str_facet = ""
    related_facet_key_list = []
    matched_facet_values = []

    enum_facet_keylist = enumerate(facets)
    for i in enum_facet_keylist:
        str_facet += str(i[0]) + "." + str(i[1]) + "," + "\n"

    example_prompt = PromptTemplate(input_variables=["input", "keylist", "explanation", "output"],
                                    template="keyword:{keyword}\nkeylist:{keylist}\nexplanation:{explanation}\noutput:{output}")
    with open("./examples.json", "r") as file:
        examples = json.loads(str(file.read()).replace("\n", "").replace("  ", ""))

    example_selector = MaxMarginalRelevanceExampleSelector.from_examples(examples, GoogleGenerativeAIEmbeddings(
        model="models/embedding-001"), FAISS, k=1)

    mmr_prompt = FewShotPromptTemplate(example_selector=example_selector, example_prompt=example_prompt,
                                       prefix="""Choose the most appropriate attributes index (more than one) from the list below for the provided keyword.Don't provide Explanation, and the output must be from the keylist.\n consider thebelow example""",
                                       suffix="keyword: {long_tail}\nkeylist:\n{key_list}\nOutput:\n\n Don't return any sentence just index numbers with comma separate",
                                       input_variables=["long_tail", "key_list"])

    print("*******Getting into getFewshort***********")

    chain = mmr_prompt | llm
    llm_response = chain.invoke({"long_tail": long_tail, "key_list": str_facet}).strip().split(",")
    for index in llm_response:
        related_facet_key_list.append(facets[int(index)])
        matched_facet_values.append(values[int(index)])
    print(f"Related facet_key for {long_tail} is  {related_facet_key_list}")
    print(f"Matched facet_values for {long_tail} is  {matched_facet_values}")
    return related_facet_key_list, matched_facet_values


def getvalues(long_tail, values):
    filter_value = []
    str_val = ""
    enum_facet_keylist = enumerate(values)
    for i in enum_facet_keylist:
        str_val += str(i[0]) + "." + str(i[1]) + "," + "\n"

    prompt = PromptTemplate.from_template("""
Choose the most appropriate attribute index number (should be only one) from the list below for the provided keyword.
keyword:{long_tail}
attribute list:
{str_val}
output : 
""")
    chain = prompt | llm
    llm_response = chain.invoke({"long_tail": long_tail, "str_val": str_val}).split(".")[0]

    return values[int(llm_response)]

