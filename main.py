from ocp_vscode import show_object

from cad.parts.sphere import make_sphere


def main() -> None:
    part = make_sphere()
    show_object(part, name="sphere")


if __name__ == "__main__":
    main()
