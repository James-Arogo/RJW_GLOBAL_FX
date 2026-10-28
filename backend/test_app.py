from flask import Flask, jsonify, render_template

# Create minimal Flask app for testing
app = Flask(__name__, template_folder='templates')

@app.route("/")
def home():
    return jsonify({"message": "Test app is working!"})

@app.route("/test-template")
def test_template():
    """Test template rendering."""
    return render_template('verify_email.html')

@app.route("/verify-email")
def verify_email_page():
    """Email verification page."""
    return render_template('verify_email.html')

if __name__ == "__main__":
    print("🚀 Starting minimal test app...")
    print("📁 Template folder:", app.template_folder)
    print("✅ Templates exist:", __import__('os').path.exists('templates'))
    print("🌐 App will run on http://127.0.0.1:4000")
    app.run(host="0.0.0.0", port=4000, debug=True)
