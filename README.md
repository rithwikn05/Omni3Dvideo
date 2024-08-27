We will be documenting our research on text-to-video generation

# Generating Video:
1. MTurker labeling data:
- Video, Description, Rating
e.g. .mp4, I want a cube rotate by 260 degree horizontally?
- Rating:
  - Is this video describing the .... [Yes, No]
  - Quality of video: how the quality of the video

Main Table: 
[Ours] ChatGPT, GPT4o(mini), LLama3.1 | Stability AI, Runaway, Pica, ...

*(not right now)
Compare something deeper about the generating methods
- Efficiency
- Variant (Conditional generating/Editing)
- Objects scene supported (drawback)


# USDMethods

- Import Assets
  - Hard code (Rithwik)
  - Add asset to the cloud and search ops (Yizhou)
Goal: e.g. "battery" -> "search database" -> return "battery_005.usd" for s3 bucket

- Scene components
  - Create basic gemetries (Yizhou [one example], finish the rest of them)
    e.g. Create a backdrop/background plane
  - Create camera look at (Yizhou)
  - Materials (Yizhou)
  
- Animation (Rithwik)
  - Key frame animation
    (Specific animation)
  - **Abstract** animation
    (Close look, slightly rotate, [Optional])

- Layout components (place something)
  - Xform (translate, rotate, scale) (Rithwik)
  - **Abstract**:
    - on?under?
    - face? 
-
-
