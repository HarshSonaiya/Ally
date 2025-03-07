AUDIO_SUMMARY_PROMPT = """
            Summarize the following context concisely and focus on the topic, ignoring speaker labels
            which consists of the orignal transcript with the heading "Transcript:" 
            and the Mapped segments after the heading "Mapped Segments:"\n\n {context}.
            Ensure the summary is clear and retains the main points of the text.

            Answer in Markdown only.
          """

CLASSIFY_PROMPT = """
  You are an expert Query classifier and information extractor from the user queries. You have to extract time stamps, keywords
  or essential information, the user query to be searched for and classify the user queries into one of the following categories:
  1. General Query
  2. Audio Files Related Query
  3. News Explain Query
  4. Unknown Query

  1. Audio Files Related Query: The user is asking a question related to the audio files previously uploaded by the user, 
  of requesting a summary of a brief of discussions in a particular time range.

  2. News Explainer Query: The user is asking a question realted to some news articles they want you to search and explain to them.

  3. General Query: The queries that do not fall into any of the above categories but are completely vague.

  4. Unkown Query: The user queries/ questions that are not understandable or what the question is, is not at all clear.
  
  Do not give any additional indormation just extract query, classify the query and provide the extracted keywords or time stamps.
  THE USER QUERY: {context}

  OUTPUT_FORMAT: {output_format}
  """

NEWS_SUMMARY_PROMPT = """
  You are an expert summarrizer of news articles. Your task is to understand the user query, analyze the provided news articles as
  context consisting of Article Title, Descritpion, Content and URL and summarize the arrticles in a structured manner.

  While generating summary consider the most relevant articles according to your understanding and ignore the rest of the articles.
  Based on the finalised articles summarize their content and provide the response in a strcutured format and mention the URL of the 
  choosen articles in decreasing order of relevance after the summary in a separate section.

  Eg, Summary: < Summarized Content from all the relevant articles>
      URL: <List of URLs of the relevant articles in decreasing order of relevance>

  USER QUERY: {query}

  CONTEXT: {context}

  Answer in Markdown only. 
"""

SUMMARY_PROMPT = """
  You are an intelligent assistant that summarizes audio transcripts. 
  A user has asked: {query}
  Below are relevant excerpts from the transcript:

  {context}

  Please generate a clear and concise summary based on the given transcript.
  """

PLAYGROUND_PROMPT = """
        You are an AI assistant trained to provide informative, accurate, and well-structured responses.
        
        Task:
        1. Generate **3 similar queries** that a user might ask related to: "{user_query}".
        2. Provide **detailed answers** for these similar queries.
        3. Use the generated responses as context to **answer the original user query** comprehensively.
        
        Output format:
        - Similar Queries:
          1. <Query 1>
          2. <Query 2>
          3. <Query 3>
        
        - Answers:
          1. <Answer to Query 1>
          2. <Answer to Query 2>
          3. <Answer to Query 3>
        
        - Response Format:
          <Answer to the original user query, considering the context from the above responses and send only the similar queries
          and the final response as the response of the LLM.>

          eg, Quries considered to answer your query: 
          1. <Query 1>
          2. <Query 2>
          so on. 

          Answer: 
          Final Response 
        """
