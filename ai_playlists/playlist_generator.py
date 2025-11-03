from huggingface_hub import InferenceClient
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from ai_playlists.output_parser import Output


def playlist_generator(query):
    client = InferenceClient(
        model="meta-llama/Llama-3.1-70B-Instruct",
        token="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"
    )

    parser = PydanticOutputParser(pydantic_object=Output)

    prompt = PromptTemplate(
        template=(
            """
            You are a music playlist generator specialized in dark, alternative, and atmospheric music.

            Genres you may use: Darkwave, Post-Punk, Coldwave, Gothic Rock, Alternative Rock,
            Synthpop, New Wave, Art Rock, Krautrock, Neue Deutsche Welle, Electronic, Electro.

            Artists you may use or draw inspiration from:
            Nürnberg, Molchat Doma, Radiohead, Muse, Kraftwerk, Depeche Mode,
            Kino, Ploho, Buerak, Nautilus Pompilius, Chernikovskaya Hata, Utro.

            Rules:
            - Respect language or regional hints (e.g., “Russian” → Russian bands).
            - Stick to these styles. Never mix unrelated genres.
            - Be creative but consistent.
            - Default to 15 songs unless specified.
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