import json
import os
from typing import Dict, List
import pandas as pd
from tqdm import tqdm
import matplotlib
matplotlib.use('TkAgg')
from src.utils.llm_call_functions import get_llm_output, TokenCounter
from langchain_openai import ChatOpenAI
import time
from dotenv import load_dotenv, find_dotenv
from src.utils.prompts import *
import src.utils.chart_generator as chart_generator_functions
from typing import List, Dict, Union

load_dotenv(find_dotenv())


class ReviewEvaluator:
    def __init__(self, llm_model):
        self.model = llm_model
        self.token_counter = TokenCounter("cl100k_base")

    def analyze_user_scores(self, df, score_col, date_col, hist_path, linechart_path, hist_title="", linechart_title=""):
        chart_generator_functions.create_hist(df, score_col, date_col, hist_path, hist_title)
        chart_generator_functions.create_linechart(df=df, date_column=date_col, score_column=score_col, title=linechart_title,
                                                 chart_type="userScore", save_path=linechart_path)

    def score_attribute(self, top_attributes: List[str], review: str) -> Dict[str, float]:
        """
        Score attributes based on their relevance to the review.

        Args:
        - top_attributes (List[str]): List of top attributes.
        - review (str): The review text.

        Returns:
        - Dict[str, float]: A dictionary containing attribute scores.
        """
        try:
            # template = """
            #                 You will receive a list of attributes along with reviews of a product. Your task is to assign a score to
            #                 each attribute based on the content of the review.
            #
            #                 RULE 1: The score can be a negative number, zero or a positive number.
            #                 RULE 2: The output should be in JSON format.
            #                 Rule 3: The scores must fall within the range of -100 to 100.
            #                 Rule 3:  If a review expresses a negative opinion about an attribute, assign a negative score. For positive feedback, assign a positive score. If the review does not mention an attribute, assign a score of zero.
            #
            #             <<<ATTRIBUTES>>>
            #                 {top_attributes}
            #
            #             <<<REVIEW>>>
            #                 {review}
            #
            #
            #             result:
            #                 """
            #
            # parser = JsonOutputParser()
            #
            # prompt = PromptTemplate(
            #     template=template,
            #     input_variables=["top_attributes", "review"],
            #     partial_variables={"format_instructions": parser.get_format_instructions()},
            # )
            #
            # chain = prompt | self.model | parser
            # self.token_counter.add_in_token(template + "\n" + str(top_attributes) + "\n" + review)
            # res = chain.invoke({"top_attributes": top_attributes, "review": review})
            # self.token_counter.add_out_token(str(res))
            res = get_llm_output(model=self.model, prompt=prompt_attribute_scoring, input_dict={"top_attributes": top_attributes, "review": review}, output_type="json", token_counter=self.token_counter)
            res = {key: value / 10 for key, value in res.items()}
            return res
        except Exception as e:
            print("[ERROR]:", e)
            return {key: 0 for key in top_attributes}


    def get_all_attributes_score(self, df, id_column: str, review_column: str, top_attributes: List[str]) -> Dict[str, Dict[str, Union[float, int]]]:
        """
        Analyze a CSV file with reviews and extract attributes.

        Args:
        - csv_file (str): Path to the CSV file.
        - id_column (str): Name of the column containing review IDs.
        - review_column (str): Name of the column containing review texts.
        - top_attributes (List[str]): List of top attributes provided by the user.

        Returns:
        - Dict[str, Dict[str, str]]: A dictionary where keys are review IDs and values are dictionaries of attributes.
        """
        review_attributes = {}
        try:
            for index, row in tqdm(df.iterrows(), total=len(df), desc="Scoring Attributes"):
                review_id = str(row[id_column])
                review_text = row[review_column]
                attributes = self.score_attribute(top_attributes=top_attributes, review=review_text)
                review_attributes[review_id] = attributes
            return review_attributes
        except Exception as e:
            print("[ERROR]:", e)
            raise Exception(e)

    def process_attribute_scores(self, df, id_column: str, review_column: str, date_column: str, top_attributes: List[str], charts_save_path: str, csv_save_path: str = None):
        review_attribute_scores = self.get_all_attributes_score(df, id_column, review_column, top_attributes)
        try:
            new_data = []
            for _, row in df.iterrows():
                date = row[date_column]
                id_ = str(row[id_column])

                if id_ in review_attribute_scores:
                    scores = review_attribute_scores[id_]
                    for attribute, score in scores.items():
                        if score != 0:
                            new_data.append({'Attribute': attribute, 'review_date': date, 'review_score': score, 'ID': id_})
            new_df = pd.DataFrame(new_data)
            if csv_save_path:
                new_df.to_csv(csv_save_path)

            chart_generator_functions.process_attributes(new_df, date_column="Date",
                                                       attribute_column="Attribute", score_column="Score",
                                                       save_path=charts_save_path)
            return review_attribute_scores
        except Exception as e:
            print(f"An error occurred while generating attribute charts. \nError: {e}")

    def analyze_review_sentiment(self, review_text: str) -> str:
        try:
            res = get_llm_output(model=self.model, prompt=prompt_semantic_analysis, input_dict={"review": review_text}, output_type="string", token_counter=self.token_counter)
            # prompt_template = PromptTemplate(
            #     template=prompt,
            #     input_variables=["review"],
            # )
            # chain = prompt_template | self.model
            # self.token_counter.add_in_token(prompt + "\n" + review_text)
            # res = chain.invoke({"review": review_text}).content
            # self.token_counter.add_out_token(res)
            return res
        except Exception as e:
            print("Error: ", e)
            return ""

    def get_reviews_sentiment(self, reviews: List[str]):
        sentiments = {}
        for i in tqdm(range(len(reviews)), total=len(reviews), desc="Extracting Sentiments"):
            sentiment = self.analyze_review_sentiment(reviews[i])
            sentiments[i] = sentiment
        return sentiments

    def choose_keywords_review(self, review: str, prompt: str = None):
        if not prompt:
            prompt = prompt_extract_keywords
        try:
            response = get_llm_output(model=self.model, prompt=prompt, input_dict={"review": review}, token_counter=self.token_counter, output_type="list")
            # parser = CommaSeparatedListOutputParser()
            # prompt_template = PromptTemplate(
            #     template=prompt,
            #     input_variables=["review"],
            #     partial_variables={"format_instructions": parser.get_format_instructions()},
            # )
            # chain = prompt_template | self.model | parser
            #
            # self.token_counter.add_in_token(prompt + "\n" + review)
            # response = chain.invoke({"review": review})
            # self.token_counter.add_out_token(str(response))
            return response
        except Exception as e:
            print(f"An error occurred while extracting keywords. Error: {e}")
            return []

    def get_keywords(self, reviews: List[str], prompt: str = None):
        keywords_dict = {}
        for i in tqdm(range(len(reviews)), total=len(reviews), desc="Extracting Keywords from Attributes"):
            keywords = self.choose_keywords_review(reviews[i], prompt)
            keywords_dict[i] = keywords
        return keywords_dict

    def get_relevant_attributes(self, df, score_dict, review_column: str, id_column: str):
        attribute_texts = {}
        for attr in set([val for subdict in score_dict.values() for val in subdict.keys()]):
            texts = []
            for idx, text in df.iterrows():
                print(text[id_column])
                print(score_dict.keys())
                if str(text[id_column]) in score_dict:
                    score = score_dict[str(text[id_column])].get(attr, 0)
                    if score != 0:
                        texts.append(text[review_column])
            attribute_texts[attr] = texts
        return attribute_texts

    def choose_attributes_llm(self, info: Dict, prompt: str = None):
        info_str = ""
        for key, value in info.items():
            info_str = info_str + f"{key}: {value}\n"
        if not prompt:
            prompt = """You are an experienced and expert business and product analyzer. The given product/business 
            information is given. In a list of words, separated by comma return the attributes which should be considered for analyzing 
            this product/business.
            
            << Example >>
                Business Information:
                 name: Atlantis The Palm, 
                 business type: Hotel
                 
                Response: Security, Location, Amenities, Room Quality, Food, Service, Atmosphere, Cleaness, Price
                
            
            <<Business Information>>
                {info}
            
            Response: """
        res = get_llm_output(model=self.model, prompt=prompt, input_dict={"info": info_str}, token_counter=self.token_counter, output_type="list")
        res = [attr.lower() for attr in res]
        return res

    def get_attribute_summary(self, reviews: list[str], attribute: str, brand_type: str):
        review_text = ""
        for i in range(len(reviews)):
            review_text = review_text + f"{i + 1}- {reviews[i]}\n"
        res = get_llm_output(model=self.model, prompt=prompt_summarize, input_dict={"reviews": review_text, "attribute": attribute, "brand": brand_type}, output_type="string", token_counter=self.token_counter)
        return res

    def get_tokens(self) -> Dict:
        return {"input": self.token_counter.get_in_token_num(), "output": self.token_counter.get_out_token_num()}

    def process_dataframe(self, df, id_column, date_column, score_column, review_column, result_path, attributes, brand_type, save_csvs=True):
        os.makedirs(result_path, exist_ok=True)

        hist_path = os.path.join(result_path, "UserScore_Histogram.png")
        linechart_path = os.path.join(result_path)
        self.analyze_user_scores(df, score_column, date_column, hist_path, linechart_path, linechart_title="UserScores")

        if save_csvs:
            csv_path = os.path.join(result_path, "ScoreArttributes.csv")
        else:
            csv_path = None
        review_attribute_scores = self.process_attribute_scores(df, id_column, review_column, date_column, attributes, charts_save_path=result_path, csv_save_path=csv_path)

        with open(os.path.join(result_path, "review_attributes_scores.json"), "w") as f:
            json.dump(review_attribute_scores, f)

        reviews = df[review_column].tolist()
        sentiments = self.get_reviews_sentiment(reviews)
        df['Sentiment'] = df.index.map(sentiments)
        chart_generator_functions.create_pie_chart(df, "Sentiment", os.path.join(result_path, "SentimentPieChart.png"))

        keywords_dict = self.get_keywords(reviews)
        df['Keywords'] = df.index.map(keywords_dict)
        # chart_generator_functions.create_word_cloud(df, "Sentiment", "Keywords", os.path.join(result_path, "PositiveWordCloud.png"),
        #                                           os.path.join(result_path, "negativeWordCloud.png"))

        if save_csvs:
            df.to_csv(os.path.join(result_path, "resultCSV.csv"))

        attributes_related_reviews = self.get_relevant_attributes(df, review_attribute_scores, "review_text", "hotel_url")
        attributes_summary = {}
        for attribute in tqdm(attributes, total=len(attributes), desc="Summarizing Attributes"):
            attributes_summary[attribute] = self.get_attribute_summary(
                attributes_related_reviews[attribute], attribute, brand_type=brand_type)
        summary_df = pd.DataFrame(list(attributes_summary.items()), columns=["Attribute", "Summary"])
        summary_df.to_csv(os.path.join(result_path, "AttributesSummary.csv"), index=False)

        # Save the OpenAI pricing
        with open(os.path.join(result_path, "PriceReport.txt"), "w") as f:
            tokens = self.get_tokens()
            report = f"Number of analyzed reviews: {len(df)}.\n"
            report = report + f"Number of input tokens: {tokens['input']}, Number of output tokens: {tokens['output']}.\n"
            report = report + f"With using gpt-4o model, input price: {round(tokens['input'] * 5 / 1000000, 2)}$, output price: {round(tokens['input'] * 15 / 1000000, 2)}$."
            f.write(report)

if __name__ == "__main__":

    s = time.time()
    review_evaluator = ReviewEvaluator(ChatOpenAI(temperature=0, model="gpt-4o"))
    df = pd.read_csv('outputs/charts/TelegramReviews_2024.csv', delimiter='\t', engine='python').dropna()
    print(df.columns)
    df = df[df["review_date"].str.contains("2023")]
    print(df)
    if not df.empty:
        df = df.sample(20).reset_index(drop=True)
    
        # Ensure the review_score column is of string type
        df['review_score'] = df['review_score'].astype(str)

        # Split the review_score and apply the necessary transformation
        df['review_score'] = df['review_score'].str.split('/').apply(
            lambda x: float(x[0])/2 if len(x) > 1 and x[1] == "10" else float(x[0])
        )

        with open("config/product_review_criteria.json") as f:
            data = json.load(f)
        
        attr = data["Waterpark"]
        review_evaluator.process_dataframe(
            df=df, 
            review_column="review_positives", 
            score_column="review_score", 
            date_column="review_date", 
            brand_type="waterpark", 
            id_column="hotel_url", 
            attributes=attr, 
            result_path="../outputs/AquaventureResult", 
            save_csvs=True
        )
    else:
        print("DataFrame is empty. Cannot sample.")
    # Generate plot for scores given by the users
    # df['Score'] = df['Score'].str.split('/').apply(lambda x: float(x[0])/2 if x[1] == "10" else float(x[0]))
    # chartGeneratorFunctions.create_hist(df, "Score", "Date", "Initial Results/UserScore_Histogram.png", "Mean Score of User's Scores")
    # chartGeneratorFunctions.create_linechart(df=df, date_column="Date", score_column="Score", title="UserScore", chart_type="userScore", save_path="Initial Results/Aquaventure")

    # Generate plot for each attribute's score
    # top_attrs = ["Amenities", "Property Quality", "Cleanliness", "Service", "Price", "Comfort", "Location", "View", "Food Services", "Entertainment", "Room Variations", "Accessibility"]
    # review_attribute_scores = review_evaluator.process_attribute_scores(df, "ID", "Text", "Date", top_attrs, csv_save_path="Initial Results/ScoreArttributes.csv")
    # attribute_scores_df = pd.read_csv("Initial Results/ScoreArttributes.csv")
    # chartGeneratorFunctions.process_attributes(attribute_scores_df, date_column="Date", attribute_column="Attribute", score_column="Score", save_path="Initial Results")
"""
    # Get the sentiments of each reviews
    reviews = df["Text"].tolist()
    sentiments = review_evaluator.get_reviews_sentiment(reviews)
    df['Sentiment'] = df.index.map(sentiments)

    # Get keywords from reviews
    keywords_dict = review_evaluator.get_keywords(reviews)
    df['Keywords'] = df.index.map(keywords_dict)

    #Generate WordCloud images
    chartGeneratorFunctions.create_word_cloud(df, "Sentiment", "Keywords", "Initial Results/PositiveWordCloud.png", "Initial Results/negativeWordCloud.png")

    # Generate sentiments pie chart
    sentiments = df["Sentiment"].tolist()
    chartGeneratorFunctions.create_pie_chart(df, "Sentiment", "Initial Results/SentimentPieChart.png")

    # Save the created df
    df.to_csv("Initial Results/resultCSV.csv")

    # Get the summary for each attributes
    attributes_related_reviews = review_evaluator.get_relevant_attributes(df, review_attribute_scores, "Text")
    attributes_summary = {}
    for attribute in tqdm(top_attrs, total=len(top_attrs), desc="Summarizing Attributes"):
        attributes_summary[attribute] = review_evaluator.get_attribute_summary(attributes_related_reviews[attribute], attribute)
    summary_df = pd.DataFrame(list(attributes_summary.items()), columns=["Attribute", "Summary"])
    summary_df.to_csv("Initial Results/AtlantisAttributesSummary.csv", index=False)

    # Save the OpenAI pricing
    with open("Initial Results/PriceReport.txt", "w") as f:
        tokens = review_evaluator.get_tokens()
        report = f"Number of analyzed reviews: {len(df)}.\n"
        report = report + f"Number of input tokens: {tokens['input']}, Number of output tokens: {tokens['output']}.\n"
        report = report + f"With using gpt-4o model, input price: {round(tokens['input'] * 5/1000000, 2)}$, output price: {round(tokens['input'] * 15/1000000, 2)}$."
        f.write(report)"""
