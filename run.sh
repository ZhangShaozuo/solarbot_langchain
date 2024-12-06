python solo_main.py \
    --user_input "How long is the lifespan of solar panels?" \
    --expert_input "" \
    --style None \
    --generation_model "openai"

# python solo_main.py \
#     --embed_model openai \
#     --generation_model openai \
#     --splitter semantic \
#     --breakpoint_threshold_type standard_deviation
    
# python db_build.py \
# 	--embed_model openai \
# 	--embed_model openai \
# 	--splitter semantic \
# 	--breakpoint_threshold_type standard_deviation

# curl -X POST "http://127.0.0.1:8000/query" \
# -H "Content-Type: application/json" \
# -d '{
#   "user_input": "Resident has feedback that the solar panel in front of his block has been there for a long time. Resident shared that TC informed him that it will be removed in November 2020, but the resident mentioned that it is still there.",
#   "expert_input": "",
#   "style": "email",
#   "vector_store": "FAISS",
#   "splitter": "semantic",
#   "embed_model": "openai",
#   "generation_model": "openai",
#   "chunk_size": 250,
#   "chunk_overlap": 50,
#   "breakpoint_threshold_type": "gradient"
# }'
