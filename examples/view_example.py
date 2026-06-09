from ocp_vscode import show_object

from cad.parts.example_ocp_text import make_example_ocp_text


def main() -> None:
    part = make_example_ocp_text()
    show_object(part, name="example_ocp_text")


if __name__ == "__main__":
    main()
