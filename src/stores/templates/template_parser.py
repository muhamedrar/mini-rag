class TemplateParser:
    def __init__(self, template: str):
        self.template = template

    def parse(self, **kwargs) -> str:
        return self.template.format(**kwargs)