# ai_person.py

import json
import os
from transformers import pipeline, Pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional

class AiPerson:
    def __init__(
        self,
        name: str,
        prompt: str,
        model_name: str,
        model_saved_locally: bool = False,
        model_path: Optional[str] = None
    ):
        """
        Initializes the AiPerson with a name, prompt, and model.

        Args:
            name (str): The name of the AI person.
            prompt (str): The initial prompt for the chatbot.
            model_name (str): The Hugging Face model identifier.
            model_saved_locally (bool): Indicates if the model is saved locally.
            model_path (str, optional): Path to the locally saved model.
        """
        self.name = name
        self.prompt = prompt
        self.model_name = model_name
        self.model_saved_locally = model_saved_locally
        self.model_path = model_path
        self.generator = self.load_model()
        self.history = []  # To keep track of the conversation

    def load_model(self) -> Pipeline:
        """
        Loads the specified Hugging Face model using a pipeline.

        Returns:
            Pipeline: The transformers pipeline for text generation.
        """
        try:
            if self.model_saved_locally and self.model_path:
                print(f"Loading model from local path '{self.model_path}'...")
                generator = pipeline(
                    'text-generation',
                    model=self.model_path,
                    device=0 if torch.cuda.is_available() else -1  # Use GPU if available
                )
                print(f"Model loaded from '{self.model_path}' successfully.")
            else:
                print(f"Loading model '{self.model_name}' from Hugging Face...")
                generator = pipeline(
                    'text-generation',
                    model=self.model_name,
                    device=0 if torch.cuda.is_available() else -1  # Use GPU if available
                )
                print(f"Model '{self.model_name}' loaded successfully.")
            return generator
        except Exception as e:
            print(f"Error loading model '{self.model_name}': {e}")
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
                pad_token_id=self.generator.tokenizer.eos_token_id,
                # You can adjust generation parameters here
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                do_sample=True
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
            "model_name": self.model_name,
            "model_saved_locally": self.model_saved_locally,
            "model_path": self.model_path
        }
        with open(f"{self.name}.json", "w") as f:
            json.dump(data, f, indent=4)
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
                ai_person = AiPerson(
                    data['name'],
                    data['prompt'],
                    data['model_name'],
                    data.get('model_saved_locally', False),
                    data.get('model_path')
                )
                print(f"AI person '{name}' loaded successfully.")
                return ai_person
        except FileNotFoundError:
            print(f"Error: {name}.json file not found.")
            return None
        except KeyError as e:
            print(f"Error: missing key in {name}.json: {e}")
            return None

    def modify(
        self,
        new_name: Optional[str] = None,
        new_prompt: Optional[str] = None,
        new_model_name: Optional[str] = None,
        save_model_locally: Optional[bool] = None
    ):
        """
        Modifies the attributes of the AI person.

        Args:
            new_name (str, optional): New name for the AI person.
            new_prompt (str, optional): New prompt for the AI person.
            new_model_name (str, optional): New model name for the AI person.
            save_model_locally (bool, optional): Whether to save the new model locally.
        """
        if new_name:
            print(f"Changing name from '{self.name}' to '{new_name}'.")
            self.name = new_name

        if new_prompt:
            print(f"Updating prompt.")
            self.prompt = new_prompt

        if new_model_name:
            print(f"Updating model from '{self.model_name}' to '{new_model_name}'.")
            self.model_name = new_model_name
            self.model_saved_locally = False
            self.model_path = None
            self.generator = self.load_model()

        if save_model_locally is not None:
            if save_model_locally and not self.model_saved_locally:
                self.save_model_locally()
            elif not save_model_locally and self.model_saved_locally:
                print(f"Model is currently saved locally at '{self.model_path}'.")
                confirm = input("Do you want to remove the local model? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    self.remove_local_model()
                    self.model_saved_locally = False
                    self.model_path = None
            else:
                print("No changes to model local storage.")

    def save_model_locally(self, save_directory: str = "models"):
        """
        Saves the model locally to the specified directory.

        Args:
            save_directory (str): Directory where the model will be saved.
        """
        try:
            os.makedirs(save_directory, exist_ok=True)
            local_model_path = os.path.join(save_directory, self.model_name.replace('/', '_'))
            print(f"Saving model '{self.model_name}' locally to '{local_model_path}'...")
            # Download and save the model and tokenizer
            model = AutoModelForCausalLM.from_pretrained(self.model_name)
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model.save_pretrained(local_model_path)
            tokenizer.save_pretrained(local_model_path)
            self.model_saved_locally = True
            self.model_path = local_model_path
            # Reload the generator from the local path
            self.generator = self.load_model()
            print(f"Model saved locally at '{local_model_path}'.")
        except Exception as e:
            print(f"Error saving model locally: {e}")

    def remove_local_model(self):
        """
        Removes the locally saved model from the filesystem.
        """
        if self.model_path and os.path.exists(self.model_path):
            try:
                import shutil
                print(f"Removing local model at '{self.model_path}'...")
                shutil.rmtree(self.model_path)
                print("Local model removed successfully.")
            except Exception as e:
                print(f"Error removing local model: {e}")
        else:
            print("No local model found to remove.")
