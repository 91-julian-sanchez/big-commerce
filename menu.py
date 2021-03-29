from __future__ import print_function, unicode_literals
from PyInquirer import prompt, Separator
from examples import custom_style_2


class CliMenu:
    
    def __init__(self, name=None, message=None, choices=None, questions=None):
        if questions is not None:
            self.questions = questions
        else:
            self.questions = [
                {
                    'type': 'list',
                    'name': name,
                    'message': message,
                    'choices': choices,
                    # 'filter': lambda val: val.lower()
                },
            ]
            
    def start(self):
        answers = prompt(self.questions, style=custom_style_2)
        return answers
    # def get_delivery_options(answers):
    #     options = ['bike', 'car', 'truck']
    #     if answers['size'] == 'jumbo':
    #         options.append('helicopter')
    #     return options

    

from pprint import pprint

def get_delivery_options(answers):
    options = ['bike', 'car', 'truck']
    if answers['size'] == 'jumbo':
        options.append('helicopter')
    return options

if __name__ == '__main__':
    # questions = [
    #     {
    #         'type': 'list',
    #         'name': 'marketplace',
    #         'message': 'Que marketplace quieres scrapear?',
    #         'choices': [
    #             'Mercadolibre',
    #             'Linio',
    #         ],
    #         'filter': lambda val: val.lower()
    #     },
    #     # {
    #     #     'type': 'list',
    #     #     'name': 'size',
    #     #     'message': 'What size do you need?',
    #     #     'choices': ['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
    #     #     'filter': lambda val: val.lower()
    #     # },
    #     # {
    #     #     'type': 'list',
    #     #     'name': 'delivery',
    #     #     'message': 'Which vehicle you want to use for delivery?',
    #     #     'choices': get_delivery_options,
    #     # },
    # ]
  
    # questions = [
    #     {
    #         'type': 'list',
    #         'name': 'theme',
    #         'message': 'What do you want to do?',
    #         'choices': [
    #             'Ask for opening hours',
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             'Ask two',
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #             {
    #                 'name': 'Contact support',
    #                 'disabled': 'Unavailable at this time'
    #             },
    #         ]
    #     },
    #     # {
    #     #     'type': 'list',
    #     #     'name': 'theme',
    #     #     'message': 'What do you want to do?',
    #     #     'choices': [
    #     #         'Order a pizza',
    #     #         'Make a reservation',
    #     #         Separator(),
    #     #         'Ask for opening hours',
    #     #         {
    #     #             'name': 'Contact support',
    #     #             'disabled': 'Unavailable at this time'
    #     #         },
    #     #         'Talk to the receptionist'
    #     #     ]
    #     # },
    #     # {
    #     #     'type': 'list',
    #     #     'name': 'size',
    #     #     'message': 'What size do you need?',
    #     #     'choices': ['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
    #     #     'filter': lambda val: val.lower()
    #     # },
    #     # {
    #     #     'type': 'list',
    #     #     'name': 'delivery',
    #     #     'message': 'Which vehicle you want to use for delivery?',
    #     #     'choices': get_delivery_options,
    #     # },
    # ]

    # climenu = CliMenu(questions=questions)
    # print(climenu.start())
    # answers = prompt(questions, style=custom_style_2)
    # pprint(answers)
    
    # questions = [
    #     {
    #         'type': 'confirm',
    #         'message': 'Do you want to continue?',
    #         'name': 'continue',
    #         'default': True,
    #     },
    #     {
    #         'type': 'confirm',
    #         'message': 'Do you want to exit?',
    #         'name': 'exit',
    #         'default': False,
    #     },
    # ]

    # answers = prompt(questions, style=custom_style_2)
    # pprint(answers)
    
    # questions - 
    questions = [
        {
            'type': 'expand',
            'message': 'Conflict on `file.js`: ',
            'name': 'overwrite',
            'default': 'a',
            'choices': [
                {
                    'key': 'y',
                    'name': 'Overwrite',
                    'value': 'overwrite'
                },
                {
                    'key': 'a',
                    'name': 'Overwrite this one and all next',
                    'value': 'overwrite_all'
                },
                {
                    'key': 'd',
                    'name': 'Show diff',
                    'value': 'diff'
                },
                Separator(),
                {
                    'key': 'x',
                    'name': 'Abort',
                    'value': 'abort'
                }
            ]
        }
    ]

    answers = prompt(questions, style=custom_style_2)
    print(answers)