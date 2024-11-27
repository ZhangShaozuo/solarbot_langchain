python cms_main.py \
    --embed_model openai \
    --generation_model openai \
    --splitter recursive \
    --chunk_size 250 \
    --chunk_overlap 50

## optimized parameters
# python cms_main.py \
#     --embed_model openai \
#     --generation_model openai \
#     --splitter semantic \
#     --breakpoint_threshold_type standard_deviation
    
# python db_build.py \
# 	--embed_model openai \
# 	--embed_model openai \
# 	--splitter semantic \
# 	--breakpoint_threshold_type standard_deviation