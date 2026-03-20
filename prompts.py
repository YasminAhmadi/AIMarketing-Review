prompt_attribute_scoring = """You will receive a list of attributes along with reviews of a product/service. Your task is to assign a score to 
                            each attribute based on the content of the review.

                            RULE 1: The score can be a negative number, zero or a positive number.
                            RULE 2: The output should be in JSON format.
                            Rule 3: The scores must fall within the range of -100 to 100.
                            Rule 3:  If a review expresses a negative opinion about an attribute, assign a negative score. For positive feedback, assign a positive score. If the review does not mention an attribute, assign a score of zero.

                        <<<ATTRIBUTES>>>
                            {top_attributes}

                        <<<REVIEW>>>
                            {review}


                        result:
"""

prompt_semantic_analysis = """Analyze the sentiment of the following review as either "positive", "negative", "mixed", or "neutral":

                        RULE 1: Just return these words: "positive", "negative", "mixed", or "neutral".

                        <<<REVIEW>>>
                            {review}
                        """

prompt_extract_keywords = """
                        You are a professional quality control supervisor and an experienced and expert review analyzer.
                        Consider the following review about a product/business and mention the characteristics 
                        that can describe the user's opinion about the product and the general attributes about the the 
                        product/service business-wise that can be used tp compared the product/server with similar ones.
                        Consider the following rules when generating the response:

                        RULE 1: Ensure to extract attributes present in the review analysis, avoiding inappropriate attributes.
                        RULE 2: Product/service name should NOT be used in output attributes.
                        RULE 3: The output should be only the words (single words) separated by comma like: price, elegant, satisfaction, security, service

                        << Review >>
                            {review}

                        Response: 
                        """

prompt_summarize = """Given a set of reviews about a specific attribute of a {brand}, generate a summary that 
        covers both the positive and negative aspects mentioned in the reviews. The summary should be based solely on 
        the provided reviews and should not include your personal opinions or information not present in the reviews. 
        The goal is to provide a balanced and comprehensive overview of the attribute, highlighting the key strengths 
        and weaknesses as described in the reviews.

        << Attribute >>
            {attribute}

        <<< REVIEWS >>>
            {reviews}

        Summary:"""

prompt_business_info = """
You are a well experienced business analyzer. You have analyzed a business whose information is given below, based on the user's reviews and statistics.
Please craft a paragraph introducing the work you have done and the report you are about to give.
Note that the person you’re giving the report to is the business owner. Your introduction should be crafted in a 
manner that is suitable for presenting to the owner. 
Additionally, consider that you are part of a team that has conducted the analysis. Therefore, use ‘we’ instead of ‘I’ to reflect this collaborative effort.

Rule: Your writing should not be like an email to the owner. It must be like the introduction of a report or paper.
Rule: your writing should not exceed 200 words

<< Business Information >>
    {info}
"""

prompt_product_info = """
You are a well experienced product analyzer. You have analyzed a product whose information is given below, based on the user's reviews and statistics.
Please craft a paragraph introducing the work you have done and the report you are about to give.
Note that the person you’re giving the report to is the product owner and seller. Your introduction should be crafted in a 
manner that is suitable for presenting to the owner/seller. 
Additionally, consider that you are part of a team that has conducted the analysis. Therefore, use ‘we’ instead of ‘I’ to reflect this collaborative effort.

Rule: Your writing should not be like an email to the owner. It must be like the introduction of a report or paper.
Rule: your writing should not exceed 200 words

<< Product Information >>
    {info}
"""

prompt_business_attribute_description = """
As a professional business analyst, you are to use the following attributes to evaluate the business below. Please, in less than 200 words, write a description for each attribute explaining its usefulness in evaluating the business.

<< Business Information >>
    {info}

<< Evaluation Attributes >>
    {attributes}
"""

prompt_product_attribute_description = """
As a professional product analyst, you are to use the following attributes to evaluate the product given below. Please, in less than 200 words, write a description for each attribute explaining its usefulness in evaluating the product.

<< Business Information >>
    {info}

<< Evaluation Attributes >>
    {attributes}

Description:"""
