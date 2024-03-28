# Simulating Diverse Patient Populations Using Patient Vignettes and Large Language Models

This repository contains source code, data, and results for the paper "Simulating Diverse Patient Populations Using Patient Vignettes and Large Language Models", presented at the [CL4Health](https://bionlp.nlm.nih.gov/cl4health2024/#) Workshop at LREC-COLING 2024. 

## Files and folders
- `./data/input`: Contains the pre-defined patient vignettes.
- `./data/output`: Contains the results of the model predictions, comparing the answers based on each of the three vignettes.

## Set-up
1. Install pdm on your machine.
2. Run `pdm install` to install the dependencies.
3. Create an account at [OpenAI](https://platform.openai.com/) and get an API key.
3. Run `pdm run-app` to spin-up a local server.

## Using the tool
1. Open your browser and navigate to `http://localhost:8501`.
2. Enter the API key you received from OpenAI.
3. Select one of the two OpenAI models. More details to be found [here](https://platform.openai.com/docs/models/overview).
3. Select one of the pre-defined patient vignettes or create your own.
4. Interact with the model.


## Deployment of UI
1. Export dependencies with `pdm export -o requirements.txt --without-hashes` (Streamlit does currently not support pdm).
2. Build docker image.
3. Run docker container. Server port: 8501.