import json
import os
from transformers import pipeline, Pipeline
import torch

class AiPerson:
    def __init__(self, name: str, prompt: str, model_name: str):
        """
        Initializes the AiPerson with a name, prompt, and model.
        
        Args:
            name (str): The name of the AI person.
            prompt (str): The initial prompt for the chatbot.
            model_name (str): The Hugging Face model identifier.
        """
        self.name = name
        self.prompt = prompt
        self.model_name = model_name
        self.generator = self.load_model(model_name)
        self.history = []  # To keep track of the conversation

    def load_model(self, model_name: str) -> Pipeline:
        """
        Loads the specified Hugging Face model using a pipeline.
        
        Args:
            model_name (str): The Hugging Face model identifier.
            
        Returns:
            Pipeline: The transformers pipeline for text generation.
        """
        try:
            print(f"Loading model '{model_name}'...")
            generator = pipeline(
                'text-generation',
                model=model_name,
                device=0 if torch.cuda.is_available() else -1  # Use GPU if available
            )
            print(f"Model '{model_name}' loaded successfully.")
            return generator
        except Exception as e:
            print(f"Error loading model '{model_name}': {e}")
            raise e

    def chat(self, user_input: str) -> str:
        """
        Generates a response based on the user's input using the loaded model.
        
        Args:
            user_input (str): The input from the user.
            
        Returns:
            str: The AI's response.
        """
        # Append user input to history
        self.history.append(f"User: {user_input}")

        # Construct the prompt
        conversation = "\n".join(self.history)
        full_prompt = f"{self.prompt}\n{conversation}\n{self.name}:"

        try:
            # Generate a response
            response = self.generator(
                full_prompt,
                max_length=500,
                num_return_sequences=1,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )

            # Extract and clean the generated text
            generated_text = response[0]['generated_text']
            # Remove the prompt and previous conversation
            generated_response = generated_text[len(full_prompt):].strip()
            # Optionally, split by newline if the model generates multiple lines
            generated_response = generated_response.split('\n')[0]

            # Append AI response to history
            self.history.append(f"{self.name}: {generated_response}")

            return f"{self.name}: {generated_response}"
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"{self.name}: I'm sorry, I couldn't process that."

    def save(self):
        """
        Saves the AI person's configuration to a JSON file.
        """
        data = {
            "name": self.name,
            "prompt": self.prompt,
            "model_name": self.model_name
        }
        with open(f"{self.name}.json", "w") as f:
            json.dump(data, f)
        print(f"AI person '{self.name}' saved successfully.")

    @staticmethod
    def load(name: str):
        """
        Loads an AI person from a JSON file.
        
        Args:
            name (str): The name of the AI person to load.
            
        Returns:
            AiPerson or None: The loaded AiPerson object or None if failed.
        """
        try:
            with open(f"{name}.json", "r") as f:
                data = json.load(f)
                ai_person = AiPerson(data['name'], data['prompt'], data['model_name'])
                print(f"AI person '{name}' loaded successfully.")
                return ai_person
        except FileNotFoundError:
            print(f"Error: {name}.json file not found.")
            return None
        except KeyError as e:
            print(f"Error: missing key in {name}.json: {e}")
            return None

def create_ai_person() -> AiPerson:
    """
    Prompts the user to create a new AI person.
    
    Returns:
        AiPerson: The created AI person.
    """
    prompt = input("Enter the prompt for the chatbot: ")
    name = input("Enter the name for the chatbot: ")
    model = input("Enter the Hugging Face model for the chatbot (e.g., 'gpt2'): ")
    return AiPerson(name, prompt, model)

def list_ai_persons() -> list:
    """
    Lists all saved AI persons.
    
    Returns:
        list: A list of AI person filenames.
    """
    ai_persons = [f for f in os.listdir() if f.endswith(".json")]
    if not ai_persons:
        print("No AI persons created yet.")
        return []
    print("Available AI Persons:")
    for ai_person in ai_persons:
        print(f"- {ai_person[:-5]}")
    return ai_persons

def main():
    """
    The main function that drives the command-line interface.
    """
    while True:
        print("\nHere are your options:")
        print("1. Create a new AI person")
        print("2. List AI persons")
        print("3. Chat with an AI person")
        print("4. Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            ai_person = create_ai_person()
            ai_person.save()
        elif choice == "2":
            list_ai_persons()
        elif choice == "3":
            ai_persons = list_ai_persons()
            if not ai_persons:
                continue
            selected = input("Enter the name of the AI person you want to chat with: ")
            ai_person = AiPerson.load(selected)
            if ai_person:
                print(f"Starting chat with {ai_person.name}. Type 'quit' to exit.")
                while True:
                    user_input = input("User: ")
                    if user_input.lower() == "quit":
                        print(f"Ending chat with {ai_person.name}.")
                        break
                    response = ai_person.chat(user_input)
                    print(response)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
