import os
import openai
from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
from data import data  # Import your state data dictionary from the 'data' module

# Load environment variables
load_dotenv()

app = Flask(__name__)
state_data = data  # Use the imported state data

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Route to display the input form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        position = request.form.get("position")
        region = request.form.get("region").lower()

        # Redirect to the strategy page with user input
        if region not in state_data:
            # Flash an error message and redirect to the same form
            print(region + "is not a valid state name. Please enter a valid state.")
            return redirect(url_for("index"))

        return redirect(url_for("get_strategy", position=position, region=region))

    return render_template("index.html")

# Route to process the strategy request and generate the speech
@app.route("/strategy")
def get_strategy():
    position = request.args.get("position", "unknown")
    region = request.args.get("region", "unknown")

    # Retrieve the state-specific summary or use a fallback if not found
    
    
    state_summary = state_data.get(
        region, 
        "This state has a diverse population with a focus on key issues like jobs, healthcare, and education."
    )

    region = region.title()

    # Create a customized prompt using the state summary and user’s position
    prompt = (
        f"You are a political speechwriter. Write a detailed 200-word campaign speech "
        f"for a candidate running on a {position} platform in {region}. "
        f"The voters in {region} care about the following: {state_summary}. "
        "Ensure the speech emphasizes these priorities, reflects the local values, "
        "and concludes with a compelling call to action encouraging voter turnout."
    )
    

    try:
        # Call the OpenAI API to generate the speech
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" for better quality if available
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500  # Adjust to ensure speech length
        )

        speech = response.choices[0].message['content'].strip()

        # Render the speech with styling
        return f"""
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Campaign Speech for {region}</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background: linear-gradient(135deg, #4CAF50, #81C784);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    max-width: 800px;
                    text-align: center;
                }}
                h1 {{
                    color: #2E7D32;
                    margin-bottom: 20px;
                }}
                p {{
                    font-size: 18px;
                    line-height: 1.6;
                    margin-bottom: 20px;
                }}
                .back-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 8px;
                    text-decoration: none;
                    font-size: 16px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }}
                .back-button:hover {{
                    background-color: #388E3C;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Campaign Speech for {region}</h1>
                <p>{speech}</p>
                <a href="/" class="back-button">Back to Form</a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        # Display an error message if something goes wrong
        return f"<h1>Error:</h1><p>{str(e)}</p>", 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
