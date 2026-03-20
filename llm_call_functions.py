import random
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser, CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import datetime
import tiktoken
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


class TokenCounter:
    def __init__(self, encoding_name):
        self.encoding_name = encoding_name
        self.in_token_number = 0
        self.out_token_number = 0

    def add_in_token(self, text):
        num = num_tokens_from_string(text, self.encoding_name)
        self.in_token_number += num

    def get_in_token_num(self):
        return self.in_token_number

    def add_out_token(self, text):
        num = num_tokens_from_string(text, self.encoding_name)
        self.out_token_number += num

    def get_out_token_num(self):
        return self.out_token_number


def get_date(date):
    model = ChatOpenAI(temperature=0)
    prompt = """Just return the start and end dates of the period in which the given date falls, separated by a comma, 
    without any additional explanations. Follow the provided examples.
     
     Rule: The output MUST ONLY be TWO dates separated by comma.
    
    << Example >>
    1)
        today's date: 2022-02-18
        relative date: two weeks ago
        target date: 2022-01-30, 2022-02-05
    2)
        today's date: 2023-06-02
        relative date: three months ago
        target date: 2023-02-02, 2022-03-02
    
    
    today's date: """ + str(datetime.datetime.today().date()) + """
    relative date: {date}
    target date:"""
    # print(date)
    dates = get_llm_output(model=model, prompt=prompt, input_dict={"date": date}, output_type="list")
    # print(dates)
    start_date = datetime.datetime.strptime(dates[0], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(dates[1], '%Y-%m-%d')

    # Calculate the difference in days between the two dates
    time_diff = end_date - start_date
    days_diff = time_diff.days

    # Generate a random number of days
    random_days = random.randrange(days_diff + 1)

    # Calculate the random date by adding the random number of days to the start date
    random_date = start_date + datetime.timedelta(days=random_days)
    random_date_str = random_date.strftime('%Y-%m-%d')
    return random_date_str


def get_llm_output(model, prompt: str, input_dict: dict, token_counter: TokenCounter = None, output_type: str = "string"):
    keys = list(input_dict.keys())
    if output_type.lower() == "json":
        parser = JsonOutputParser()
        prompt_template = PromptTemplate(
            template=prompt,
            input_variables=keys,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt_template | model | parser
    elif output_type.lower() == "list":
        parser = CommaSeparatedListOutputParser()
        prompt_template = PromptTemplate(
            template=prompt,
            input_variables=keys,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt_template | model | parser
    elif output_type.lower() == "string":
        prompt_template = PromptTemplate(
            template=prompt,
            input_variables=keys,
        )
        chain = prompt_template | model
    else:
        raise ValueError(f"{output_type} is not a supported output type!")
    if token_counter:
        input_str = ""
        for val in input_dict.values():
            input_str = input_str + str(val) + "\n"
        token_counter.add_in_token(prompt + "\n" + input_str)
    if output_type.lower() == "string":
        res = chain.invoke(input_dict).content
    else:
        res = chain.invoke(input_dict)
    if token_counter:
        token_counter.add_out_token(str(res))
    return res


if __name__ == "__main__":
    df = pd.read_csv("Initial Results/resultCSV.csv")
    print(df['Sentiment'].value_counts())
