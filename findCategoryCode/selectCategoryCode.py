from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import json

load_dotenv()
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = GoogleGenerativeAI(model="gemini-pro")


def getcategoryCode(long_tail):
    global name
    print("******* Please wait..... Searching Category code *******")
    with open("./category.json", "r") as file:
        new_data = json.loads(str(file.read()).replace("\n", "").replace("  ", ""))
        full_category_name_list = [i["name"] for i in new_data]

    vectorstore = FAISS.from_texts(full_category_name_list, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    relevant_category_name = retriever.get_relevant_documents(long_tail)

    prompt = PromptTemplate.from_template("""Select the most suitable category name from the below category list for the provided keyword.

Keyword: {long_tail}

category list : cate{category_list}

Do not add any extra content. For example, if the keyword is "Bluestar 1.5 TON AC", the answer should be "Air Conditioner". Even if "AC" falls under the "Home Appliances" category, it should be categorized under "Air Conditioner", which is the most suitable category.
JBL earphone should be audio-video/headphones-earphones/earphones and bluetooth earphone should be /audio-video/headphones-earphones/bluetooth-headphones
For instance, for the keyword "Sony home theaters and soundbars", the answer would be "/audio-video/home-theatres-sound-bars/sound-bars".
        """)

    chain = prompt | llm
    llm_output = chain.invoke(
        {"long_tail": long_tail, "category_list": [i.page_content + " " for i in relevant_category_name]})
    code = 0
    for details in new_data:
        if details["name"] == llm_output:
            code = details["_id"]
            name = details["name"]
    print(f"Thanks for waiting. The category code for {long_tail} is {name}/{code}")
    return code
