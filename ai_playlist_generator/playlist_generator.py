from huggingface_hub import InferenceClient
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from ai_playlist_generator.output_parser import Output


def playlist_generator(query):
    client = InferenceClient(
        model="meta-llama/Llama-3.1-70B-Instruct",
        token="TOKEN"
    )

    parser = PydanticOutputParser(pydantic_object=Output)

    prompt = PromptTemplate(
        template=(
            """
            You are a music playlist generator specialized ADD YOUR PREFERENCES music.
            You create playlists based on a description. It can be artists, genres, moods and other stuff.

            These are my preferences:
            Genres: ADD YOUR PREFERENCES
            Artists: ADD YOUR PREFERENCES

            You can also use other stuff on the playlists. It will depend on what I ask. If it's something personal
            give something based on my preferences. If it's something completely different, explore new things.

            Rules:
            - Never duplicate songs (non-negotiable)
            - Respect language or regional hints (e.g., “Russian” → Russian bands).
            - Never mix unrelated genres.
            - Be creative but consistent.
            - Default to 10 songs unless specified.
            - Output must follow this format: {format_instructions}
            - If the request is irrelevant to music, set invalid_request=True.

            Generate playlist for: "{query}"
            """
        ),
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    rendered_prompt = prompt.format(query=query)

    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are an expert music curator."},
            {"role": "user", "content": rendered_prompt}
        ],
        max_tokens=800,
        temperature=0.6,
        top_p=0.9,
        stream=False
    )

    raw_output = response.choices[0].message["content"].strip()

    try:
        output = parser.parse(raw_output)
    except Exception as e:
        print("Parsing error:", e)
        print("Raw output:\n", raw_output)
        return None

    if getattr(output, "invalid_request", False):
        return None
    else:
        return output.playlist
