from xml.dom.minidom import parse
from pprint import pprint as pp
import pandas as pd

import os
import os.path


class XML_Document:
    """Reads a given XML document.

    Can provide a list of all variables, project variables, and a dict of dialogues and variables."""

    def __init__(self, filename: str) -> None:
        self.document = parse(filename)

    def get_all_vars(self) -> list[str]:
        """Returns a list of all variable names in the document."""
        return [
            variable.attributes["name"].value
            for variable in [
                *self.document.getElementsByTagName("hd:text"),
                *self.document.getElementsByTagName("hd:number"),
                *self.document.getElementsByTagName("hd:trueFalse"),
            ]
        ]

    def get_all_dialogs(self) -> dict:
        """Returns a dictionary of {dialog name: [variable names]} in the document."""
        return {
            dialog.attributes["name"].value: [
                variable.attributes["name"].value
                for variable in dialog.getElementsByTagName("hd:item")
            ]
            for dialog in self.document.getElementsByTagName("hd:dialog")
        }

    def get_project_vars(self) -> list[str]:
        """Returns a list of every variable in the document that isn't in a dialog."""
        return [
            var
            for var in self.get_all_vars()
            if var
            not in [var for dialog in self.get_all_dialogs().values() for var in dialog]
        ]

    def to_xlsx_WIP(self) -> None:
        # create xlsx from a template with same name as document
        # create a bulk upload settings sheet
        # create a project sheet with project parameters and default units
        # create another sheet for every dialog, with the dialog parameters and default units
        pass


def cmps_to_xlsx(document_names):

    list_ = []
    for document_name in document_names:

        document = XML_Document(document_name)
        dialogs = document.get_all_dialogs()
        dialogs["project"] = document.get_project_vars()

        for dialog in dialogs:

            for parameter in dialogs[dialog]:
                try:
                    document_name = document_name.split("\\")[-1]
                except:
                    pass
                list_.append((dialog, parameter, document_name))

    with pd.ExcelWriter("HotDocs Dialogs.xlsx") as writer:
        pd.DataFrame(list_).to_excel(
            writer, sheet_name="Report Parameters", index=False, header=False
        )


def main():
    document_names = []
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".cmp")]:
            document_names.append(os.path.join(dirpath, filename))

    cmps_to_xlsx(document_names)


if __name__ == "__main__":
    main()
