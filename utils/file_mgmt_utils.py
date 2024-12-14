from os import path, makedirs


def create_outputs_folder():
    """
    Creates an outputs folder if it does not exist.
    """
    try:
        if not path.exists("outputs"):
            makedirs("outputs")
    except Exception as e:
        print(f"create_outputs_folder failed due to this error:\n{e}")
        raise