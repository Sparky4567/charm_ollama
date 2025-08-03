import subprocess
import ollama
from datetime import datetime
import os

def get_models():
    """Gets the list of available Ollama models."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        models = [line.split()[0] for line in lines[1:]]
        return models
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Could not get Ollama models. Make sure Ollama is running.")
        return []

def choose_model(models):
    """Lets the user choose a model using gum."""
    if not models:
        return None
    try:
        process = subprocess.Popen(['gum', 'choose'] + models, stdout=subprocess.PIPE)
        choice, _ = process.communicate()
        return choice.decode('utf-8').strip()
    except FileNotFoundError:
        print("Error: 'gum' is not installed. Please install it to use this application.")
        return None

def save_conversation(conversation):
    """Saves the conversation to a Markdown file."""
    try:
        save_process = subprocess.run(['gum', 'confirm', 'Save conversation?'], stdout=subprocess.PIPE, text=True)
        if save_process.returncode == 0:
            now = datetime.now()
            filename = now.strftime("%Y_%m_%d_%H%M%S") + ".md"
            filepath = os.path.join('storage', filename)

            with open(filepath, 'w') as f:
                for message in conversation:
                    f.write(f"**{message['role'].capitalize()}**:\n\n{message['content']}\n\n---\n\n")
            print(f"Conversation saved to {filepath}")
    except FileNotFoundError:
        print("Error: 'gum' is not installed. Please install it to use this application.")


def main():
    """Main function to run the chat application."""
    models = get_models()
    if not models:
        return

    chosen_model = choose_model(models)
    if not chosen_model:
        return

    print(f"Starting chat with {chosen_model}. Type 'exit' or 'quit' to end.")

    conversation = []
    while True:
        try:
            user_input_process = subprocess.run(['gum', 'input', '--placeholder', 'You: '], capture_output=True, text=True)
            user_input = user_input_process.stdout.strip()
        except FileNotFoundError:
            print("Error: 'gum' is not installed. Please install it to use this application.")
            return

        if user_input.lower() in ['exit', 'quit']:
            break

        conversation.append({"role": "user", "content": user_input})

        try:
            spinner = subprocess.Popen(['gum', 'spin', '--spinner', 'dots', '--title', 'Ollama is thinking...'])
            response = ollama.chat(
                model=chosen_model,
                messages=conversation
            )
            spinner.terminate()
            # Wait for spinner to terminate to avoid overlapping output
            spinner.wait()


            assistant_response = response['message']['content']
            # A simple way to format the output to be more readable
            print(f"\nAssistant:")
            # Use gum to format the output in a nice way.
            subprocess.run(['gum', 'format', '--', assistant_response])
            conversation.append({"role": "assistant", "content": assistant_response})

        except ollama.ResponseError as e:
            spinner.terminate()
            spinner.wait()
            print(f"Error: {e.error}")


    if conversation:
        save_conversation(conversation)

if __name__ == "__main__":
    main()
