import string
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import spacy

class TextNormalization:
    def __init__(self):
        # Initialize tokenizer and Spacy lemmatizer
        self.regexp = RegexpTokenizer(r"[\w']+")
        self.spacy_lemmatizer = spacy.load("en_core_web_sm", disable=['parser', 'ner'])

        # Ensure the necessary nltk data packages are downloaded
        #nltk.download('stopwords')
        #nltk.download('averaged_perceptron_tagger')

        # Combine all types of stopwords
        self.allstops = self._get_all_stopwords()

    def _get_all_stopwords(self):
        # Define additional stopwords and categories
        stops = stopwords.words("english")
        addstops = ["among", "onto", "shall", "thrice", "thus", "twice", "unto", "us", "would"]
        prepositions = ["about", "above", "across", "after", "against", "among", "around", "at", "before", "behind", "below", "beside", "between", "by", "down", "during", "for", "from", "in", "inside", "into", "near", "of", "off", "on", "out", "over", "through", "to", "toward", "under", "up", "with"]
        prepositions_less_common = ["aboard", "along", "amid", "as", "beneath", "beyond", "but", "concerning", "considering", "despite", "except", "following", "like", "minus", "onto", "outside", "per", "plus", "regarding", "round", "since", "than", "till", "underneath", "unlike", "until", "upon", "versus", "via", "within", "without"]
        coordinating_conjunctions = ["and", "but", "for", "nor", "or", "so", "and", "yet"]
        correlative_conjunctions = ["both", "and", "either", "or", "neither", "nor", "not", "only", "but", "whether", "or"]
        subordinating_conjunctions = ["after", "although", "as", "as if", "as long as", "as much as", "as soon as", "as though", "because", "before", "by the time", "even if", "even though", "if", "in order that", "in case", "in the event that", "lest", "now that", "once", "only", "only if", "provided that", "since", "so", "supposing", "that", "than", "though", "till", "unless", "until", "when", "whenever", "where", "whereas", "wherever", "whether or not", "while"]
        return stops + addstops + prepositions + prepositions_less_common + coordinating_conjunctions + correlative_conjunctions + subordinating_conjunctions

    def convert_to_lowercase(self, text):
        # Convert text to lowercase
        return text.lower()

    def remove_whitespace(self, text):
        # Remove leading and trailing whitespaces
        return text.strip()

    def remove_punctuation(self, text):
        # Remove punctuation from text, keeping contractions intact
        punct_str = string.punctuation
        punct_str = punct_str.replace("'", "")  # Discarding apostrophe from the string to keep contractions intact
        return text.translate(str.maketrans("", "", punct_str))

    def remove_stopwords(self, text):
        # Remove stopwords from text using a tokenizer
        return " ".join([word for word in self.regexp.tokenize(text) if word not in self.allstops])

    def text_lemmatizer(self, text):
        # Lemmatize text using SpaCy
        text_spacy = " ".join([token.lemma_ for token in self.spacy_lemmatizer(text)])
        return text_spacy

    def discard_non_alpha(self, text):
        # Discard non-alphabetic words from text
        word_list_non_alpha = [word for word in self.regexp.tokenize(text) if word.isalpha()]
        text_non_alpha = " ".join(word_list_non_alpha)
        return text_non_alpha

    def keep_pos(self, text):
        # Keep words with specific parts-of-speech tags
        tokens = self.regexp.tokenize(text)
        tokens_tagged = nltk.pos_tag(tokens)
        keep_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'FW', 'PRP', 'PRPS', 'RB', 'RBR', 'RBS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WPS', 'WRB']
        keep_words = [x[0] for x in tokens_tagged if x[1] in keep_tags]
        return " ".join(keep_words)

    def text_normalizer(self, text):
        # full text normalization pipeline
        text = self.convert_to_lowercase(text)
        text = self.remove_whitespace(text)
        text = self.remove_punctuation(text)
        text = self.remove_stopwords(text)
        # text = self.text_lemmatizer(text)  # Uncomment if you want to include lemmatization
        text = self.discard_non_alpha(text)
        text = self.keep_pos(text)
        return text
