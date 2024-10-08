# main.py

import json
import os
from server.ai_person import AiPerson

def create_ai_person() -> AiPerson:
    """
    Prompts the user to create a new AI person.

    Returns:
        AiPerson: The created AI person.
    """
    prompt = input("Enter the prompt for the chatbot: ").strip()
    name = input("Enter the name for the chatbot: ").strip()
    model = input("Enter the Hugging Face model for the chatbot (e.g., 'gpt2'): ").strip()

    # Ask if the user wants to save the model locally
    while True:
        save_locally_input = input("Do you want to save the model locally? (yes/no): ").strip().lower()
        if save_locally_input in ['yes', 'no']:
            save_locally = save_locally_input == 'yes'
            break
        else:
            print("Please enter 'yes' or 'no'.")

    if save_locally:
        # Define the directory to save models
        save_directory = "models"
        # Initialize AiPerson without local model info
        ai_person = AiPerson(name, prompt, model)
        # Save model locally
        ai_person.save_model_locally(save_directory)
    else:
        ai_person = AiPerson(name, prompt, model)

    return ai_person

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

def modify_ai_person():
    """
    Allows the user to modify an existing AI person.
    """
    ai_persons = list_ai_persons()
    if not ai_persons:
        return

    selected = input("Enter the name of the AI person you want to modify: ").strip()
    ai_person = AiPerson.load(selected)
    if not ai_person:
        return

    print("Enter new values or press Enter to keep existing values.")

    new_name = input(f"New name (current: {ai_person.name}): ").strip()
    new_name = new_name if new_name else None

    new_prompt = input(f"New prompt (current: {ai_person.prompt}): ").strip()
    new_prompt = new_prompt if new_prompt else None

    new_model = input(f"New model (current: {ai_person.model_name}): ").strip()
    new_model = new_model if new_model else None

    # Handle model saving preference
    save_locally = None
    if new_model:
        while True:
            save_locally_input = input("Do you want to save the new model locally? (yes/no): ").strip().lower()
            if save_locally_input in ['yes', 'no']:
                save_locally = save_locally_input == 'yes'
                break
            else:
                print("Please enter 'yes' or 'no'.")

    # Modify the AiPerson
    ai_person.modify(
        new_name=new_name,
        new_prompt=new_prompt,
        new_model_name=new_model,
        save_model_locally=save_locally
    )

    # If the name was changed, save the configuration with the new name and remove the old JSON
    if new_name:
        ai_person.save()
        old_json = f"{selected}.json"
        if os.path.exists(old_json):
            os.remove(old_json)
    else:
        ai_person.save()

def main():
    """
    The main function that drives the command-line interface.
    """
    while True:
        print("\nHere are your options:")
        print("1. Create a new AI person")
        print("2. List AI persons")
        print("3. Modify an AI person")
        print("4. Chat with an AI person")
        print("5. Quit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            ai_person = create_ai_person()
            ai_person.save()
        elif choice == "2":
            list_ai_persons()
        elif choice == "3":
            modify_ai_person()
        elif choice == "4":
            ai_persons = list_ai_persons()
            if not ai_persons:
                continue
            selected = input("Enter the name of the AI person you want to chat with: ").strip()
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
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
