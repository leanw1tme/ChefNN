from transformers import FlaxAutoModelForSeq2SeqLM, AutoTokenizer
import os

token = os.getenv("HF_TOKEN")

MODEL = "onlymylvl/T5-recipe"
tokenizer = AutoTokenizer.from_pretrained(MODEL, use_fast=True, use_auth_token=token)
model = FlaxAutoModelForSeq2SeqLM.from_pretrained(MODEL, use_auth_token=token)

prefix = "items: "
generation_kwargs = {
    "max_length": 512,
    "min_length": 64,
    "do_sample": True,
    "top_k": 60,
    "top_p": 0.95
}

special_tokens = tokenizer.all_special_tokens
tokens_map = {
    "<sep>": "--",
    "<section>": "\n"
}

def skip_special_tokens(text, special_tokens):
    for token in special_tokens:
        text = text.replace(token, "")
    return text

def target_postprocessing(texts, special_tokens):
    if not isinstance(texts, list):
        texts = [texts]
    
    new_texts = []
    for text in texts:
        text = skip_special_tokens(text, special_tokens)
        for k, v in tokens_map.items():
            text = text.replace(k, v)
        new_texts.append(text)
    return new_texts

def generation_function(texts):
    _inputs = texts if isinstance(texts, list) else [texts]
    inputs = [prefix + inp for inp in _inputs]
    inputs = tokenizer(
        inputs, 
        max_length=256, 
        padding="max_length", 
        truncation=True, 
        return_tensors="jax"
    )

    input_ids = inputs.input_ids
    attention_mask = inputs.attention_mask

    generated_recipes = []
    for i in range(input_ids.shape[0]):
        output_ids = model.generate(
            input_ids=input_ids[i:i+1],
            attention_mask=attention_mask[i:i+1],
            **generation_kwargs
        )
        generated = output_ids.sequences
        generated_recipe = target_postprocessing(
            tokenizer.batch_decode(generated, skip_special_tokens=False),
            special_tokens
        )
        generated_recipes.extend(generated_recipe)
    
    return generated_recipes

# async def format_and_send_recipe(text: str, message):
#     sections = text.split("\n")
#     for section in sections:
#         section = section.strip()
#         headline = None

#         if section.startswith("title:"):
#             section = section.replace("title:", "").strip().capitalize()
#             headline = "🍽 TITLE"
#             await message.answer(f"[{headline}]: {section}")
#         elif section.startswith("ingredients:"):
#             section = section.replace("ingredients:", "")
#             headline = "🧂 INGREDIENTS"
#             section_info = [f"  • {info.strip().capitalize()}" for info in section.split("--")]
#             await message.answer(f"[{headline}]:\n" + "\n".join(section_info))
#         elif section.startswith("directions:"):
#             section = section.replace("directions:", "")
#             headline = "👨‍🍳 DIRECTIONS"
#             section_info = [f"  {i+1}. {info.strip().capitalize()}" for i, info in enumerate(section.split("--"))]
#             await message.answer(f"[{headline}]:\n" + "\n".join(section_info))
#     recipe_text += "-" * 130
#     await message.answer(recipe_text)

async def format_and_send_recipe(text: str, message):
    sections = text.split("\n")
    recipe_parts = []

    for section in sections:
        section = section.strip()
        if section.startswith("title:"):
            section = section.replace("title:", "").strip().capitalize()
            recipe_parts.append(f"🍽 TITLE: {section}")
        elif section.startswith("ingredients:"):
            section = section.replace("ingredients:", "")
            items = [f"  • {info.strip().capitalize()}" for info in section.split("--")]
            recipe_parts.append("🧂 INGREDIENTS:\n" + "\n".join(items))
        elif section.startswith("directions:"):
            section = section.replace("directions:", "")
            steps = [f"  {i+1}. {info.strip().capitalize()}" for i, info in enumerate(section.split("--"))]
            recipe_parts.append("👨‍🍳 DIRECTIONS:\n" + "\n".join(steps))

    full_message = ("-" * 60) + "\n" + "\n\n".join(recipe_parts) + "\n" + ("-" * 60)

    MAX_LENGTH = 4096
    for i in range(0, len(full_message), MAX_LENGTH):
        await message.answer(full_message[i:i+MAX_LENGTH])