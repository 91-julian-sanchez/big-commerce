from __future__ import print_function, unicode_literals
from PyInquirer import prompt, Separator
from examples import custom_style_2


class CliMenu:
    
    def __init__(self, questions):
        print("CliMenu.__init__()")
        self.questions = questions
        
    def start(self):
        answers = prompt(self.questions, style=custom_style_2)
        return answers
    # def get_delivery_options(answers):
    #     options = ['bike', 'car', 'truck']
    #     if answers['size'] == 'jumbo':
    #         options.append('helicopter')
    #     return options

    

if __name__ == '__main__':
    questions = [
        {
            'type': 'list',
            'name': 'marketplace',
            'message': 'Que marketplace quieres scrapear?',
            'choices': [
                'Mercadolibre',
                'Linio',
            ],
            'filter': lambda val: val.lower()
        },
        # {
        #     'type': 'list',
        #     'name': 'size',
        #     'message': 'What size do you need?',
        #     'choices': ['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
        #     'filter': lambda val: val.lower()
        # },
        # {
        #     'type': 'list',
        #     'name': 'delivery',
        #     'message': 'Which vehicle you want to use for delivery?',
        #     'choices': get_delivery_options,
        # },
    ]
    climenu = CliMenu(questions)
    print(climenu.start())