def validate_float(textfield):
    """
    This function can be called by an on_text-callback of any textfield. It ensures, that the user is only able to input strings that can be converted into a valid float afterwards
    """

    # empty inputs do not have to be validated
    if textfield.text.strip() == "":
        textfield.text = ""
        textfield.error = True
        return

    # Make sure that the input is a number and separated by a dot
    try:
        textfield.text = textfield.text.replace(",", ".").strip()
        float(textfield.text)
    except:
        if not textfield.text == "-":
            textfield.text = textfield.text[:-1]
            return
    textfield.error = False
    return


def validate_int(textfield):
    """
    This function can be called by an on_text-callback of any textfield. It ensures, that the user is only able to input strings that can be converted into a valid integer afterwards
    """

    # empty inputs do not have to be validated
    if textfield.text.strip() == "":
        textfield.text = ""
        textfield.error = True
        return

    # Make sure that the input is an integer
    try:
        int(textfield.text)
    except:
        textfield.text = textfield.text[:-1]
        return
    textfield.error = False
    return
