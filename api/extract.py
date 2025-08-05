import os
import textwrap

import langextract as lx

# 1. Define the prompt and extraction rules
prompt = textwrap.dedent("""\
    Extract characters, emotions, and relationships in order of appearance.
    Use exact text for extractions. Do not paraphrase or overlap entities.
    Provide meaningful attributes for each entity to add context.""")

# 2. Provide a high-quality example to guide the model
examples = [
    lx.data.ExampleData(
        text="ROMEO. But soft! What light through yonder window breaks? It is the east, and Juliet is the sun.",
        extractions=[
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="ROMEO",
                attributes={"emotional_state": "wonder"}
            ),
            lx.data.Extraction(
                extraction_class="emotion",
                extraction_text="But soft!",
                attributes={"feeling": "gentle awe"}
            ),
            lx.data.Extraction(
                extraction_class="relationship",
                extraction_text="Juliet is the sun",
                attributes={"type": "metaphor"}
            ),
        ]
    )
]


def extract(text: str):
    extractions = lx.extract(
        text_or_documents=text,
        prompt_description=prompt,
        examples=examples,
        language_model_type=lx.inference.OpenAILanguageModel,
        language_model_params={"base_url": os.environ.get(
            "LANGEXTRACT_API_MODEL_URL")},
        model_id=os.environ.get("LANGEXTRACT_API_MODEL_ID"),
        fence_output=False,
        use_schema_constraints=False,
    )
    return lx.data_lib.annotated_document_to_dict(extractions)
