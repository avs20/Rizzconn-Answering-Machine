import gradio as gr
import requests
from mvp import tbl
import sqlite3

# # Function to call your system API and get the response
# def search_question(question):
#     # Replace 'your_system_api_url' with the actual API endpoint
#     api_url = 'your_system_api_url'
#     try:
#         response = requests.post(api_url, json={"question": question})
#         response.raise_for_status()  # Raise an HTTPError for bad responses
#         return response.json().get('answer', 'No answer found.')
#     except Exception as e:
#         return f"Error: {str(e)}"

# Function to handle feedback submission
def handle_feedback(feedback, additional_feedback):
    # Process the feedback as needed
    return "Thank you for your feedback!"

from mvp import search_question



# Define the Gradio interface
def gradio_app():
    with gr.Blocks() as demo:

        # Header
        gr.Markdown("# RizzCon Anwering Machine")
        # Textbox for question input
        question_input = gr.Textbox(label="Enter your question:", lines=2, placeholder="Type your question here...")
        
        # Button to submit question
        search_button = gr.Button("Search")
        
        # Output box for showing the result
        # Output box for showing the result
        # result_output = gr.Dataframe(label="Answers",wrap = True, headers=["Text", "Filename", "Username"], datatype=["str", "str", "str"], visible=False)
        result_output = gr.Markdown(label="Answers", visible=False)
        
        # Feedback question
        feedback_question = gr.Markdown("Did the result answer your question?", visible=False)
        
        # Thumbs up and down buttons
        thumbs_up = gr.Button("👍", visible=False)
        thumbs_down = gr.Button("👎", visible=False)
        
        # Optional text box for additional feedback on thumbs down
        additional_feedback = gr.Textbox(label="Please provide specific feedback:", lines=2, placeholder="Type your feedback here...", visible=False)
        
        # Submit button for feedback
        feedback_button = gr.Button("Submit Feedback", visible=False)
        
        # Function to show the feedback options and answer after search
        # Function to show the feedback options and answer after search
        def show_feedback_and_answer(answer):
            return (
                gr.update(visible=True),  # result_output
                gr.update(visible=True),  # feedback_question
                gr.update(visible=True),  # thumbs_up
                gr.update(visible=True),  # thumbs_down
                gr.update(visible=True)   # feedback_button
            )
        
        # Function to show the additional feedback textbox
        def show_additional_feedback_box():
            return gr.update(visible=True)
        

        def format_results(docs):
            return [[doc.text, doc.filename, doc.username] for doc in docs]
        
        
        search_button.click(
            fn=search_question, 
            inputs=question_input, 
            outputs=result_output
        ).then(
            fn=show_feedback_and_answer, 
            inputs=None, 
            outputs=[result_output, feedback_question, thumbs_up, thumbs_down, feedback_button]
        )
        
        thumbs_down.click(fn=show_additional_feedback_box, outputs=additional_feedback)
        
        # Connect the feedback button to the handle_feedback function
        feedback_button.click(fn=handle_feedback, inputs=[thumbs_down, additional_feedback], outputs=None)
    
    return demo

# Launch the Gradio app
if __name__ == "__main__":
    gradio_app().launch()
