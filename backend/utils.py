def get_form_error_msg(form):
    error_msg = ''
    for key in form.errors:
        error_msg = form.errors[key][0]
        break
    return error_msg
