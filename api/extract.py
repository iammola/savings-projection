import os
import textwrap

import langextract as lx

# 1. Define the prompt and extraction rules
prompt = textwrap.dedent("""\
    Extract the following financial information:
    - Currency, i.e the ISO 4217 currency code and symbol
    - Initial account balance
    - Monthly contributions
    - Monthly withdrawals
    - Interest rate tiers, including the amount ranges and the rates

    For each monetary value, extract the raw numerical value without currency symbols or commas and decimals.
    For each percentage rate value, extract the raw numerical value without the percent sign
    The extraction should include exact text from the input. Do not paraphrase or overlap entities.
    Provide meaningful attributes for each entity to add context, such as currency, tier amounts, and rate percentages as applicable.
""")

# 2. Provide a high-quality example to guide the model
examples = [
    lx.data.ExampleData(
        text="I started with $4,000 and contribute $1,000 monthly, but I also take out $250 per month. The tiers are: 0.25% on balances under $10,000, then 0.3% up to $25,000, then 0.55% up to $100,000, 0.8% up to $500,000, and 1% for anything more than that.",
        extractions=[
            lx.data.Extraction(
                extraction_class="currency",
                extraction_text="$",
                attributes={"symbol": "$", "code": "USD"}
            ),
            lx.data.Extraction(
                extraction_class="initial_balance",
                extraction_text="$4,000",
                attributes={"amount": "4000", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="monthly_contribution",
                extraction_text="$1,000",
                attributes={"amount": "1000", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="monthly_withdrawal",
                extraction_text="$250",
                attributes={"amount": "250", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="0.25% on balances under $10,000",
                attributes={"tier_min": "0",
                            "tier_max": "10000", "rate": "0.25", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="0.3% up to $25,000",
                attributes={"tier_min": "10000",
                            "tier_max": "25000", "rate": "0.3", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="0.55% up to $100,000",
                attributes={"tier_min": "25000",
                            "tier_max": "100000", "rate": "0.55", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="0.8% up to $500,000",
                attributes={"tier_min": "100000",
                            "tier_max": "500000", "rate": "0.8", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="1% for anything more than that",
                attributes={"tier_min": "500000",
                            "tier_max": "infinity", "rate": "1", "link_to": "currency"}
            ),
        ]
    ),
    lx.data.ExampleData(
        text="My starting balance was $5,000, and I contribute $800 every month. I also take out $150 monthly for expenses. The interest rate structure is as follows: 0.2% for balances below $5,000, 0.5% up to $20,000, 1% up to $100,000, and 1.5% for balances above $100,000.",
        extractions=[
            lx.data.Extraction(
                extraction_class="currency",
                extraction_text="$",
                attributes={"symbol": "$", "code": "USD"}
            ),
            lx.data.Extraction(
                extraction_class="initial_balance",
                extraction_text="$5,000",
                attributes={"amount": "5000", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="monthly_contribution",
                extraction_text="$800",
                attributes={"amount": "800", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="monthly_withdrawal",
                extraction_text="$150",
                attributes={"amount": "150", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="0.2% for balances below $5,000",
                attributes={"tier_min": "0",
                            "tier_max": "5,000", "rate": "0.2"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="0.5% up to $20,000",
                attributes={"tier_min": "5000",
                            "tier_max": "20000", "rate": "0.5", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="1% up to $100,000",
                attributes={"tier_min": "20000",
                            "tier_max": "100000", "rate": "1", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="1.5% for balances above $100,000",
                attributes={"tier_min": "100000",
                            "tier_max": "infinity", "rate": "1.5", "link_to": "currency"}
            ),
        ]
    ),
    lx.data.ExampleData(
        text="My balance began at $50,000, and I contribute $3,000 every month. I also withdraw $1,500 per month. The interest rates are 0.4% for balances below $50,000, 0.6% up to $200,000, 1% from $200,000 to $1 million, and 1.5% for balances exceeding $1 million.",
        extractions=[
            lx.data.Extraction(
                extraction_class="currency",
                extraction_text="$",
                attributes={"symbol": "$", "code": "USD"}
            ),
            lx.data.Extraction(
                extraction_class="initial_balance",
                extraction_text="$50,000",
                attributes={"amount": "50000", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="monthly_contribution",
                extraction_text="$3,000",
                attributes={"amount": "3000", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="monthly_withdrawal",
                extraction_text="$1,500",
                attributes={"amount": "1500", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="0.4% for balances below $50,000",
                attributes={"tier_min": "0",
                            "tier_max": "50000", "rate": "0.4"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="0.6% up to $200,000",
                attributes={"tier_min": "50000",
                            "tier_max": "200000", "rate": "0.6"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="1% from $200,000 to $1 million",
                attributes={"tier_min": "200000",
                            "tier_max": "1000000", "rate": "1"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="1.5% for balances exceeding $1 million",
                attributes={"tier_min": "1000000",
                            "tier_max": "infinity", "rate": "1.5"}
            ),
        ]
    ),
    lx.data.ExampleData(
        text="I started with $5,000, and I contribute $300 every month. The interest rates are: up to $10,000 at 0.25%, then $50,000 at 0.5%, and anything more than that gets 1%.",
        extractions=[
            lx.data.Extraction(
                extraction_class="currency",
                extraction_text="$",
                attributes={"symbol": "$", "code": "USD"}
            ),
            lx.data.Extraction(
                extraction_class="initial_balance",
                extraction_text="$5,000",
                attributes={"amount": "5000", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="monthly_contribution",
                extraction_text="$300",
                attributes={"amount": "300", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="up to $10,000 at 0.25%",
                attributes={"tier_min": "0",
                            "tier_max": "10000", "rate": "0.25"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="$50,000 at 0.5%",
                attributes={"tier_min": "10000",
                            "tier_max": "50000", "rate": "0.5"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="anything more than that gets 1%",
                attributes={"tier_min": "50000",
                            "tier_max": "infinity", "rate": "1"}
            ),
        ]
    ),
    lx.data.ExampleData(
        text="Starting balance was €10,000. I take out €500 each month. The interest rate structure is: 0.3% for up to €10,000, then €100,000 at 0.6%, and balances over that get 1%.",
        extractions=[
            lx.data.Extraction(
                extraction_class="currency",
                extraction_text="€",
                attributes={"symbol": "€", "code": "EUR"}
            ),
            lx.data.Extraction(
                extraction_class="initial_balance",
                extraction_text="€10,000",
                attributes={"amount": "10000", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="monthly_withdrawal",
                extraction_text="€500",
                attributes={"amount": "500", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="0.3% for up to €10,000",
                attributes={"tier_min": "0",
                            "tier_max": "10000", "rate": "0.3"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="€100,000 at 0.6%",
                attributes={"tier_min": "10000",
                            "tier_max": "100000", "rate": "0.6"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="balances over that get 1%",
                attributes={"tier_min": "100000",
                            "tier_max": "infinity", "rate": "1"}
            ),
        ]
    ),
    lx.data.ExampleData(
        text="I started with CA$100,000. Every month, I take out CA$5,000 but don't make any contributions. The interest rates are: up to CA$50,000 at 0.6%, then CA$200,000 at 1%, and above that at 1.5%.",
        extractions=[
            lx.data.Extraction(
                extraction_class="currency",
                extraction_text="CA$",
                attributes={"symbol": "CA$", "code": "CAD"}
            ),
            lx.data.Extraction(
                extraction_class="initial_balance",
                extraction_text="CA$100,000",
                attributes={"amount": "100000", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="monthly_withdrawal",
                extraction_text="CA$5,000",
                attributes={"amount": "5000", "link_to": "currency"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="up to CA$50,000 at 0.6%",
                attributes={"tier_min": "0",
                            "tier_max": "50000", "rate": "0.6"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="CA$200,000 at 1%",
                attributes={"tier_min": "50000",
                            "tier_max": "200000", "rate": "1"}
            ),
            lx.data.Extraction(
                extraction_class="interest_rate_tiers",
                extraction_text="above that at 1.5%",
                attributes={"tier_min": "200000",
                            "tier_max": "infinity", "rate": "1.5"}
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
        fence_output=True,
        use_schema_constraints=False,
        debug=True
    )
    print(f"Performed extraction on \"{text}\"")
    return lx.data_lib.annotated_document_to_dict(extractions)
