import re
import warnings

import assistant
from beaupy import select, spinners
import os
import platform


def generate_response(system, message, attempt=1, max_attempts=3):
    loader = spinners.Spinner(spinners.CLOCK, "CLI helper is thinking...")
    loader.start()

    if attempt > max_attempts:
        print(f"Maximum attempts ({max_attempts}) reached. Exiting.")
        return None

    try:
        response = assistant.ask(message=message, system=system)
        loader.stop()
        return response
    except Exception:
        loader.stop()
        warnings.warn(f"Attempt {attempt} to generate a response failed.", RuntimeWarning)

        user_choice = input(f"Do you want to retry? ({attempt}/{max_attempts}) [y/N]: ").lower()
        if user_choice == 'y':
            return generate_response(system, message, attempt + 1, max_attempts)
        else:
            print("Operation cancelled by user.")
            return None


def explain_command(system_explain, prompt=""):
    if not prompt:
        prompt = input("? Which command would you like to explain?\n"
                       "    \033[90mExample: \"ls -l\"\033[0m\n\n"
                       "> ")

    explanation = generate_response(system_explain, prompt)

    if explanation:
        print("\n\nExplanation:\n")
        print(syntax_highlight(explanation) + "\n")
        options = ["✅ Run this command", "👀 Explain further", "❌ Exit"]
        action = select(options, cursor='> ', cursor_style='white').lower()

        print(f"\nYou chose to \033[94;1m{action}\033[0m.\n")

        if action == "✅ run this command":
            try:
                os.system(prompt)
                print("Command executed successfully.\nExiting...")
            except Exception as e:
                warnings.warn(f"An error occurred while running the command: {e}\n"
                              f"Exiting...", RuntimeWarning)
                return None
        elif action == "👀 explain further":
            print("How would you like to explain further?")
            options = ["🔎 Explain in more detail", "🙌 Explain more concisely", "❌ Exit"]
            action = select(options, cursor='> ', cursor_style='white').lower()

            print(f"\nYou chose to \033[94;1m{action}\033[0m.\n")

            if action == "❌ Exit":
                return
            elif action == "🔎 explain in more detail":
                explain_command(system_explain, f"Explain this command: {prompt} in more detail")
            elif action == "🙌 explain more concisely":
                explain_command(system_explain, f"Explain this command: {prompt} more concisely")
        else:
            return


def suggest_command(system_suggest, prompt="", system_explain=None):
    if not prompt:
        prompt = input("? How would you like the command to do?\n"
                       "    Example: \"list all files in a directory\"\n\n"
                       "> ")

    command = generate_response(system_suggest, prompt, max_attempts=3)

    if not command:
        print("No command was generated. Exiting.")
        return

    # Using regular expression to extract the command
    match = re.search(r'{STARTH}(.*?){ENDH}', command)
    if match:
        extracted_command = match.group(1)
        extracted_command = '{STARTH}' + extracted_command + '{ENDH}'
    else:
        print("No valid command format found. Exiting.")
        return

    print("\n\nCommand:\n")
    print("\033[1m" + syntax_highlight(extracted_command) + "\033[0m\n")

    action = select(["✅ Run this command", "❓ Explain this command", "📝 Revise query", "❌ Exit"]).lower()

    print(f"\nYou chose to \033[94;1m{action}\033[0m.\n")

    if action == "✅ run this command":
        try:
            os.system(extracted_command)
        except Exception as e:
            warnings.warn(f"An error occurred while running the command: {e}", RuntimeWarning)
            suggest_command(system_suggest, prompt)
    elif action == "❓ explain this command":
        explain_command(system_explain, extracted_command)
    elif action == "📝 revise query":
        revision_prompt = input("Revision: ")
        return suggest_command(system_suggest, f"Change this command: {extracted_command} "
                                               f"with these edits: {revision_prompt}")


def main():
    print("Welcome to the CLI Assistant!\n")

    print("\033[90mThis is a CLI assistant that helps you with your command line needs.\n"
          "It uses the OpenAI API to generate commands and explanations.\n"
          "This is a beta version, so please report any bugs to the developer @DY_L directly.\n\n"
          "Contact information: li_dongyuan@bupt.edu.cn\n"
          "\033[0m")

    operating_system = platform.system() + " " + platform.release()
    dirname = os.path.abspath(os.path.dirname(__file__))

    def os_replace(x):
        return x.replace("{OPERATING_SYSTEM}", operating_system)

    with open(os.path.join(dirname, "prompts/suggest.txt")) as f:
        system_suggest = os_replace(f.read())
    with open(os.path.join(dirname, "prompts/explain.txt")) as f:
        system_explain = os_replace(f.read())

    print("What would you like this program to do? Choose ONE option from below:\n")

    options = ["Explain a command", "Suggest a command"]
    action = select(options, cursor='> ', cursor_style='white').lower()

    print(f"\nYou chose to \033[94;1m{action}\033[0m.\n")

    if action == "explain a command":
        explain_command(system_explain)
    elif action == "suggest a command":
        suggest_command(system_suggest, system_explain=system_explain)
    else:
        print("Please select a valid option!")


def syntax_highlight(text, color="\33[93m"):
    """
    Highlights the syntax of a command to bright yellow

    :param text: The text to highlight
    :param color: Color to highlight with, defaults to bright yellow
    :return: Highlighted text
    """
    return text.replace("{STARTH}", color).replace("{ENDH}", "\033[0m")


if __name__ == "__main__":
    main()
