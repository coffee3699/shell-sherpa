import assistant
from beaupy import select, spinners
import os
import platform


def generate_response(system, message):
    loader = spinners.Spinner(spinners.CLOCK, "CLI helper is thinking...")
    loader.start()
    response = assistant.ask(message=message, system=system)
    loader.stop()

    return response


def explain_command(system_explain, prompt=""):
    if not prompt:
        prompt = input("? Which command would you like to explain?\n"
                       "    Example: \"ls -l\"\n"
                       "> ")

    explanation = generate_response(system_explain, prompt)

    if explanation:
        print("\n\nExplanation:\n")
        print(syntax_highlight(explanation) + "\n")
        action = select(["✅ Run this command", "📝 Explain further", "❌ Exit"]).lower()

        print("You chose to " + action + ".\n")

        if action == "✅ run this command":
            os.system(prompt)
        elif action == "📝 explain further":
            print("How would you like to explain further?")
            further_prompt = select(["🔎 Explain in more detail", "📎 Explain with an example", "❌ Exit"]).lower()

            print("You chose to " + further_prompt + ".")

            if further_prompt == "❌ Exit":
                return
            explain_command(system_explain, f"Explain this command: {prompt} further with: {further_prompt}")
        else:
            return


def suggest_command(system_suggest, prompt=""):
    if not prompt:
        prompt = input("? How would you like the command to do?\n"
                       "    Example: \"I want to list all files in a directory\"\n\n"
                       "> ")

    command = generate_response(system_suggest, prompt)

    if command:
        print("\n\nCommand:\n")
        print("\033[1m" + syntax_highlight(command) + "\033[0m\n")
        action = select(["✅ Run this command", "📝 Revise query", "❌ Exit"]).lower()

        print("You chose to " + action + ".\n")

        if action == "✅ run this command":
            os.system(command)
        elif action == "📝 revise query":
            revision_prompt = input("Revision: ")
            return suggest_command(system_suggest, f"Change this command: {command} "
                                                   f"with these edits: {revision_prompt}")
        else:
            return


def main():
    print("Welcome to the CLI Assistant!\n")

    print("\033[90mThis is a CLI assistant that helps you with your command line needs.\n"
          "It uses the OpenAI API to generate commands and explanations.\n"
          "This is a beta version, so please report any bugs to the developer @DY_L directly.\n\n\033[0m")

    operating_system = platform.system() + " " + platform.release()
    dirname = os.path.abspath(os.path.dirname(__file__))

    def os_replace(x):
        return x.replace("{OPERATING_SYSTEM}", operating_system)

    with open(os.path.join(dirname, "prompts/suggest.txt")) as f:
        system_suggest = os_replace(f.read())
    with open(os.path.join(dirname, "prompts/explain.txt")) as f:
        system_explain = os_replace(f.read())

    print("What would you like to do? Choose ONE option from below:\n")

    options = ["Explain a command", "Suggest a command"]
    action = select(options, cursor='> ', cursor_style='white').lower()

    print(f"\nYou chose to {action}.\n")

    if action == "explain a command":
        explain_command(system_explain)
    elif action == "suggest a command":
        suggest_command(system_suggest)
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
