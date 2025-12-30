from flask import Flask, render_template, request, jsonify
import os
import sys
import json
import logging
from lxml import etree

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from feature_extractor import FeatureExtractor
from rule_based_feedback import RuleBasedFeedbackEngine
from xml_parser import extract_methods_from_xml

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

extractor = FeatureExtractor()
engine = RuleBasedFeedbackEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audit_text', methods=['POST'])
def audit_text():
    try:
        data = request.json
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        features = extractor.extract_features(text)
        feedback = engine.generate_feedback(features)
        
        return jsonify({
            'features': features,
            'feedback': feedback
        })
    except Exception as e:
        app.logger.error(f"Error auditing text: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/audit_file', methods=['POST'])
def audit_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        content = file.read()
        
        # Try as XML first (PMC style)
        try:
            root = etree.fromstring(content)
            text = extract_methods_from_xml(root)
        except Exception:
            # Fallback to plain text
            text = content.decode('utf-8', errors='ignore')
            
        if not text:
            return jsonify({'error': 'Could not extract text from file'}), 400
            
        features = extractor.extract_features(text)
        feedback = engine.generate_feedback(features)
        
        return jsonify({
            'features': features,
            'feedback': feedback,
            'extracted_text_snippet': text[:500] + '...'
        })
    except Exception as e:
        app.logger.error(f"Error auditing file: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Increase max content length for larger XMLs
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
    print("Dashboard starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
