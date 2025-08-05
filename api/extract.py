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
    return lx.extract(
        text_or_documents=text,
        prompt_description=prompt,
        examples=examples,
        language_model_type=lx.inference.OpenAILanguageModel,
        language_model_params={"base_url": os.environ.get("LANGEXTRACT_API_MODEL_URL")},
        model_id="jan-nano-128k-Q4_K_M",
        fence_output=False,
        use_schema_constraints=False,
    )


result = extract(
    "Lady Juliet gazed longingly at the stars, her heart aching for Romeo")

# Save the results to a JSONL file
lx.io.save_annotated_documents(
    [result], output_name="extraction_results.json", output_dir=".")

# Generate the visualization from the file
html_content = lx.visualize("extraction_results.json")
with open("visualization.html", mode="w",encoding="utf8") as f:
    f.write(html_content)
