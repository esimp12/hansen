### Working

- [ ] Finish naive parameter search implementation
  - [ ] Extract keyphrases from the prompt
  - For each parameter
    - Compute the similarity to each keyphrase
    - For each keyphrase compute the similarity of each word in the keyphrase to the parameter name
      - Naively choose the phrase after the highest similarity score as the parameter value
      - Clean the parameter value for unlikely characters
    - Display the chosen parameter name and values for each parameter keyphrase combination
    - Include an option to manually supply the parameter value
    - Repeat for each parameter
- [ ] Look into converting command loop into a Command pattern
  - We want to be able to wrap and insert command into the command loop programatically and not always wait for user input
