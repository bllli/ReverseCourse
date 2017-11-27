from django import template

register = template.Library()


@register.filter(name='add_arg')
def template_args(instance, arg):
    """stores the arguments in a separate instance attribute"""
    if not hasattr(instance, "_TemplateArgs"):
        setattr(instance, "_TemplateArgs", [])
    instance._TemplateArgs.append(arg)
    return instance


@register.filter(name='call')
def template_method(instance, method):
    """retrieves the arguments if any and calls the method"""
    method = getattr(instance, method)
    if hasattr(instance, "_TemplateArgs"):
        to_return = method(*instance._TemplateArgs)
        delattr(instance, '_TemplateArgs')
        return to_return
    return method()
