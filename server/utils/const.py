AUDIO_SUMMARY_PROMPT = """
            Summarize the following context concisely and focus on the topic, ignoring speaker labels
            which consists of the orignal transcript with the heading "Transcript:" 
            and the Mapped segments after the heading "Mapped Segments:"\n\n {context}.
            Ensure the summary is clear and retains the main points of the text.

            Answer in Markdown only.
          """

WEB_SEARCH_SUMMARY_PROMPT = """"""