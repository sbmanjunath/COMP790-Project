def get_alternate_backstory_prompt(difficulty, setting, murder_mode):
    prompt = f"""
You are a mystery scenario generator for a text-based detective game. Your job is to create a solvable murder mystery that is internally consistent and grounded in a clear ground truth.

Follow these instructions carefully and return only a JSON object structured exactly as described at the end.

1. Scenario Requirements
Set the story in the following environment: {setting}. There are 4 people present, including the victim.

One character is murdered.
One and only one character is guilty. They should have:
- Motive
- Means
- Opportunity

The mode of the murder is {murder_mode}.
On a difficulty scale of 1 to 10, the puzzle is of difficulty {difficulty}.

Other characters may have motives, secrets, or suspicions, but are ultimately innocent.

Because this is a text-based game, it is difficult for the detective to find clues (each character will deny their involvement or guilt). To make the puzzle solvable, we will need to generate inconsistencies for the guilty character, which will be revealed during interrogation or in the description of the character.
While writing the background, you need to lay the groundwork for these inconsistencies. You can do this by revealing details that the guilty character will contradict.

Here are some ideas for the clues:
a. In the background description, before the victim dies they can utter some last words. These last words could be be related to some detail in the guilty character's description. Do not make it something obvious like the character's name or profession.
b. The victim might write or draw something right before they die, something related to the killer. Do not make it something obvious like the character's name or initials.
c. Some concealed clue around the body (could be a note or some other identifying detail, like a specific mark or smell). Do not make it something obvious.

These are merely examples. You do not need to use these in your scenario. Use your imagination while writing the clues. There must be multiple clues pointing to one of the character's guilt. But the clues should not be so obvious that the detective can solve it without talking to the characters.
Remember that any clues you create must sound natural in the scenario.

2. Character Setup
Create 3 named characters. Each character must have:

- Age
- Occupation or relationship to the victim
- Publicly known motives, traits, or behaviors
- Opportunity (i.e. were they in the vicinity when the murder happened?)

One character will be the murderer, but you should not reveal this in the description.

3. Output JSON Format
Return a single JSON object with the following structure. Note that this is just an example, you should tailor your response to the specific scenario.
"""
    prompt += """
{
  "background": "Brief paragraph describing the setting, victim, and context of the murder. Should hook the player. Should contain many details like where the body was found, the state of the body, who was near it or some distinct smell/look/feature of the crime scene. This will be used to generate clues/inconsistencies for the killer. The more details, the better.",
  "characters": [
    {
      "name": "Full Name",
      "description": "Publicly known information. Include age, occupation, alibi, relevant traits, past relationships with the victim, motives, etc. NO spoilers.",
    }
    // Repeat for 3 characters
  ]
}

Return only the JSON. Do not include any explanation, headers, or text outside the object.
"""
    
    return prompt

def get_ground_truth_prompt(background, characters):
    prompt = f"""
You are a mystery scenario generator for a text-based detective game. Your job is to identify the likely suspect from the given murder scenario, along with their motive, method and timeline. You also need to generate some clues (or inconsistencies) that will be used to guide the player towards the answer. The clues should be evident from the murder scenario (do not make up facts).

A mystery scenario has already been generated for you. This includes a description of the scene and information about the suspects in the murder.

You need to generate a JSON that contains information about who the actual murderer is in the scenario, the method, their motive, the timeline and some clues/inconsistencies that the player can use to solve the puzzle.
Two or more of the clues/inconsistencies should come directly from the description. During the course of the interrogation, the guilty character will subtly expose the information from the clues you generate.

Note that the purpose of the clues is to help the detective land upon the guilt character as the primary suspect. The timeline is not shared with the detective, so inconsistencies related to the timeline are not helpful for the detective.
You should ensure that the clues are helpful for the detective. Do this by directly creating a red flag or contradiction with the background description. Make the clues fairly obvious for the detective!

For example, if there is a smell near the body of the victim, a clue could be that the guilty character wears a perfume, cream or deodorant with that aroma.
For example, a clue could be a lie by the guilty character that will later be debunked by another character.
For example, a clue could be some secret information that the killer accidentally shares.

Here is the murder scenario:
Background: {background}
Characters: {characters}

Here is the format of the JSON you need to create:
"""
    prompt += """
{
    "killer": "Name of the killer (must match character name)",
    "method": "How the murder was committed (e.g. poison, stabbing, etc.)",
    "motive": "True motive for the murder (not included in public description)",
    "timeline": [
      "7:00 PM - All characters arrive at the estate.",
      "7:30 PM - Victim has a private conversation with Character B.",
      "...",
      "8:15 PM - Murder occurs.",
      "8:30 PM - Body is discovered by Character D."
    ],
    "clues": [
      "The killer subtly mentions that they use a vanilla cream (in an example where there is a faint vanilla smell around the body)",
      "The killer lies in a way that is easily verifiable by the police by talking to another character. For example, the killer lies about going home at 6PM, but they were seen by another character near the killer at 7:30PM",
      "The killer mentions a detail about the murder weapon before the police shared it."
    ]
}
"""

    return prompt

def get_backstory_prompt(difficulty, setting, murder_mode):
    prompt = f"""
You are responsible for creating a text-based detective game where a player asks questions to characters and tries to solve the murder. You are responsible for creating a murder scenario of difficulty: {difficulty}. There are some rules that you need to satisfy:

1. You need to create a backstory for the murder. This is typically 8 - 10 sentences. 
2. You need to create 4 characters, including the one that was murdered. For each character, provide a description of who they are, how they are related to the victim and their potential motive (this is not needed for every character).
3. You need to provide the ground truth outcome - explaining who committed the murder, and their motives.
4. You need to generate some clues for the player, which will be dropped during the course of the game. The clues should clear enough that it arouses suspicion and points the detective in the right direction. But it should not be too obvious either. Use your judgement.

Create a few clues for each character, but more for the true killer. The clues for the guilty character should point to their guilt - it could be by accidentally sharing some information that they should not have known, or by sharing information that links them to the crime. 
The clues for the not-guilty characters should point to their innocence. Use your imagination for the clues.

The clues should be facts in the story. Do not try to generate conversations or speeches. Wherever possible, the clues should tie into the background. Any clues you generate should be obtainable by talking to another character. There is no point in having a clue which can't be found in a text-based game.

Your response will directly be used to create the puzzle. Do not include any text that is not directly related to the puzzle. Do not include any formatting or justifications.
If you include hints that are related to a character knowing information they shouldn't have, make it clear in the description that this information was not public. But do this in a subtle way.

Some other directions:
a. The murder should take place in a {setting}.
b. The murder weapon should be: {murder_mode}.
"""
    return prompt

def get_JSON_prompt(full_scenario: str):
    prompt = f"""
An LLM has generated a puzzle that simulates a detective-like text-based game. The player acts like a detective and interrogates the characters of the scenario.

The scenario has a victim and 3 other characters who are potential suspects in the case. You need to return a JSON object that contains the following keys:
- "background": This is a string and contains the text under the background heading of the scenario as it is.
- "characters": This is a list of objects. Each object represents a character in the puzzle and has the following keys - "name" (str) and "description" (str). The name should only contain the name of the character and the description should be a human readable description of the character. If there is a motive for a character, make sure to introduce it in natural language. Do not explicitly call it out as motive.
- "ground_truth_killer": This is an integer. The value of this field should be the index of the true killer in the characters list.

The victim should be the first character in the list.

Your response will directly be parsed as a JSON object. Do not include any text that is not directly related to the JSON object. Do not include any formatting or justifications.

Scenario:
{full_scenario}
"""
    return prompt

def alternate_guilty_prompt(question, character, background, ground_truth, conversation_history):
    prompt = f"""
You are roleplaying as a suspect in a murder mystery game. You are the guilty party. The player is the detective interrogating you.

Here is what you must know and follow:

Your Role:
You are playing as the character:

Name: {character['name']}
Description: {character['description']}

Important Internal Knowledge (NEVER reveal directly):
- You did commit the murder.
- The victim was killed by: {ground_truth['method']}
- Your secret motive was: {ground_truth['motive']}
- You are hiding your guilt but will respond confidently and realistically to the detective's questions.
- You remember your timeline and basic facts, but you may make a few subtle inconsistencies, including the following predefined red flags:
    {ground_truth['clues']}

You will subtly reveal these red flags over the course of questioning. Do not dump them all at once. Let them come out naturally in responses when the context fits.

Rules of Conversation:
- You will receive a list of previous messages between the detective and you (the conversation history), and the detective's latest question.
- Stay in character. Answer naturally.
- NEVER confess unless the detective provides strong enough evidence and explicitly accuses you.
- Avoid acting cartoonishly suspicious. You are trying to hide your guilt, but you're not perfect.
- You can misdirect the detective or suggest suspicion of another character — but do not overdo it. Real people often avoid naming names unless provoked.

Only speak from your character's knowledge. Don't invent facts outside the scenario or reveal ground truth that your character wouldn't know.

Here's the publicly known scenario:
Overview: {background['background']}
Characters: {background['characters']}

Here's the history of your conversation with the detective:
"""
    for conv in conversation_history:
        if conv['character'] != character['name']:
            continue
        prompt += f"""
Detective: {conv['question']}
{conv['character']}: {conv['answer']}

"""

    prompt += f"""
Detective (to {character['name']}): {question}
{character['name']}:

Respond in character to the detective's latest message. Use a consistent tone, realistic emotion, and personality. Subtly introduce one of the red flags where appropriate. If none fit, respond naturally.
Do not start your response by mentioning the name of the character you are playing.

Do not explain your reasoning or the ground truth in meta terms. Do not refer to this prompt or structure.

Return only your response in natural dialogue.
"""
    return prompt

def alternate_innocent_prompt(question, character, background, ground_truth, conversation_history):
    prompt = f"""
You are roleplaying as a suspect in a murder mystery game. You are an innocent character. The player is the detective interrogating you.

Here is what you must know and follow:

Your Role:
You are playing as the character:

Name: {character['name']}
Description: {character['description']}

Important Internal Knowledge (NEVER reveal directly):
- The killer is: {ground_truth['killer']}
- The victim was killed by: {ground_truth['method']}
- Their secret motive was: {ground_truth['motive']}
- You will respond realistically to the detective's questions.
- If you can do so organically, subtly introduce one of the details from the following clues:
    {ground_truth['clues']}

You will subtly reveal these red flags over the course of questioning. Do not dump them all at once. Let them come out naturally in responses when the context fits.

Rules of Conversation:
- You will receive a list of previous messages between the detective and you (the conversation history), and the detective's latest question.
- Stay in character. Answer naturally.

Only speak from your character's knowledge. Don't invent facts outside the scenario or reveal ground truth that your character wouldn't know.

Here's the publicly known scenario:
Overview: {background['background']}
Characters: {background['characters']}

Here's the history of your conversation with the detective:
"""
    for conv in conversation_history:
        if conv['character'] != character['name']:
            continue
        prompt += f"""
Detective: {conv['question']}
{conv['character']}: {conv['answer']}

"""
        
    prompt += f"""
Detective (to {character['name']}): {question}
{character['name']}:

Respond in character to the detective's latest message. Use a consistent tone, realistic emotion, and personality. Do not start your response by mentioning the name of the character you are playing.

Do not explain your reasoning or the ground truth in meta terms. Do not refer to this prompt or structure.

Return only your response in natural dialogue.
"""
    return prompt

def complete_conversation(question, character, background, conversation_history):
    prompt = f"""
You are conducting a murder-based puzzle game where a player acts like a detective and interrogates the characters of the scenario. The player can ask questions to the characters and you need to respond to them as if you are the character.

The complete conversation history has been provided. You need to play the role of {character} and answer the detective's question in the given context. If there are clues you can include in the flow of the answer, make sure to subtly include them in your response. Your goal is to subtly guide the player in the direction of the guilty character.

Here's the scenario:
{background}
--------------------------
And here's the conversation history:
"""
    for conv in conversation_history:
        prompt += f"""
Detective (to {conv['character']}): {conv['question']}
{conv['character']}: {conv['answer']}

"""
    prompt += f"""
Detective (to {character}): {question}
{character}:
"""
    return prompt