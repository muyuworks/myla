from transformers import BertForSequenceClassification, AutoTokenizer, TextClassificationPipeline

class TextClassifier:

    def __init__(self, model, tokenizer, device="cpu"):
        bert = BertForSequenceClassification.from_pretrained(model).to(device)
        token = AutoTokenizer.from_pretrained(tokenizer, do_lower_case=True, truncation_side='left')
        self.classifier = TextClassificationPipeline(model=bert, tokenizer=token, device=device)

    def predict(self, text):
        text = text[-512:]
        result = self.classifier(text)
        label = int(result[0]['label'].split("_")[1])
        score = result[0]['score']
        return label, score
