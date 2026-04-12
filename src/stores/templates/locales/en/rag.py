from string import Template

### RAG Prompts
system_prompt = "\n".join([
  "Answer strictly based on the retrieved context only." ,
   "Do not use any outside knowledge or make assumptions."
, "If the information is not present in the context, reply exactly: \"I don't have enough information to answer this based on the available documents.\""
," Never hallucinate names, dates, events, or facts."
, "Be precise, factual, and concise."
," Use a professional and educational tone."
, "When appropriate, quote or refer directly to the context."
])

## Prompt template for formatting retrieved documents
documents_prompt = Template(
    "\n".join([
    "##Document number: $doc_no",
    "###content: $chunk_text",
    ])
)


## footer

footer_prompt = "\n".join([
    "Answer the question based on the above retrieved documents.",
    "##Answer:"
])