
# Module 13: Will You Get In? - GradCafe Admissions Predictor

Fine-tunes a pretrained DistilBERT model on GradCafe admissions data and serves predictions through a Flask web page.

## Setup

1. Create and activate a Python 3.12 virtual environment:
py -3.12 -m venv .venv13
..venv13\Scripts\Activate.ps1

2. Install dependencies:
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cu121

## Training the Model

python train_model.py

This loads `data/llm_extend_applicant_data_run.jsonl`, filters to Accepted/Rejected rows, fine-tunes DistilBERT for 3 epochs, evaluates on a held-out test set, and saves the model to `saved_model/`. Takes about 15 to 20 minutes on GPU.

## Running Inference
python inference.py

Loads the saved model and runs two sample predictions to confirm the reload works correctly.

## Running the Website
python run.py

Visit `http://127.0.0.1:5000/predict` for the "Will You Get In?" prediction page, or `http://127.0.0.1:5000/analysis` for the GradCafe analysis dashboard (requires a PostgreSQL connection).

## Model Details

- Base model: distilbert-base-uncased
- Max sequence length: 256
- Batch size: 16
- Epochs: 3
- Learning rate: 2e-5
- Optimizer: AdamW
- Test accuracy: 79.1 percent
- Test F1 score: 0.753


Tokenizer Choice

DistilBERT's own WordPiece tokenizer (distilbert-base-uncased) was used rather than a
custom tokenizer, since fine-tuning requires the input tokenization to exactly match
what the pretrained weights were trained on. Building a custom tokenizer would have
broken the alignment between input tokens and the pretrained embeddings, discarding
the main benefit of using a pretrained model in the first place. A max sequence length
of 256 was chosen as long enough to hold the university/program/GPA/GRE fields plus a
meaningful chunk of the comments field, without excessive padding on shorter entries.

## Project Structure

- `train_model.py`: loads data, builds the unified text template, splits train/test, fine-tunes the model, evaluates it, and saves it
- `inference.py`: loads the saved model and runs predictions
- `run.py`: starts the Flask application
- `src/app.py`: Flask routes, including the new `/predict` route
- `src/templates/predict.html`: the Will You Get In? form and results page
- `saved_model/`: fine-tuned model weights, tokenizer, and label mapping
- `data/`: source dataset

## Disclaimer

This is a class project model trained on scraped, self-reported GradCafe data. It is not a real admissions tool and should not be used for actual application decisions.