import json

class ResultCalculator:
    def __init__(self):
        self.personality_types = {
            'explorer': {
                'title': 'The Explorer',
                'description': 'You thrive on adventure and new experiences. You are curious, independent, and adaptable.',
                'traits': ['Curious', 'Independent', 'Adaptable', 'Adventurous'],
                'recommendations': ['Try rock climbing', 'Visit a new country', 'Learn a new skill', 'Join an adventure club']
            },
            'nurturer': {
                'title': 'The Nurturer',
                'description': 'You are caring, supportive, and find joy in helping others. You value harmony and relationships.',
                'traits': ['Caring', 'Supportive', 'Empathetic', 'Harmonious'],
                'recommendations': ['Volunteer for a cause', 'Join a support group', 'Practice meditation', 'Spend time in nature']
            },
            'thinker': {
                'title': 'The Thinker',
                'description': 'You are analytical, introspective, and value knowledge and understanding. You prefer depth over breadth.',
                'traits': ['Analytical', 'Introspective', 'Knowledgeable', 'Contemplative'],
                'recommendations': ['Read philosophy books', 'Take up chess', 'Join a book club', 'Learn a new language']
            },
            'leader': {
                'title': 'The Leader',
                'description': 'You are confident, decisive, and naturally take charge. You inspire others and drive results.',
                'traits': ['Confident', 'Decisive', 'Inspiring', 'Goal-oriented'],
                'recommendations': ['Take a leadership course', 'Start a project', 'Mentor someone', 'Join a professional organization']
            }
        }
    
    def calculate(self, responses):
        scores = {
            'explorer': 0,
            'nurturer': 0,
            'thinker': 0,
            'leader': 0
        }
        
        response_dict = {}
        for response in responses:
            response_dict[response.question_id] = response.answer_value
        
        # Question 4: Ideal weekend scoring
        weekend_answer = response_dict.get(4, '')
        if weekend_answer == 'Adventure outdoors':
            scores['explorer'] += 3
        elif weekend_answer == 'Cozy at home':
            scores['thinker'] += 2
        elif weekend_answer == 'Social gathering':
            scores['nurturer'] += 2
        elif weekend_answer == 'Learning something new':
            scores['thinker'] += 1
            scores['explorer'] += 1
        
        # Question 5: Introversion scoring
        introverted = response_dict.get(5, '')
        if introverted == 'yes':
            scores['thinker'] += 2
            scores['nurturer'] += 1
        else:
            scores['leader'] += 2
            scores['explorer'] += 1
        
        # Question 6: Stress handling scoring
        stress_answer = response_dict.get(6, '')
        if stress_answer == 'Talk it out with friends':
            scores['nurturer'] += 2
        elif stress_answer == 'Exercise or physical activity':
            scores['explorer'] += 2
        elif stress_answer == 'Take time alone to think':
            scores['thinker'] += 2
        elif stress_answer == 'Dive into work or projects':
            scores['leader'] += 2
        
        # Question 7: Planning vs spontaneous scoring
        planning = response_dict.get(7, '')
        if planning == 'yes':
            scores['leader'] += 1
            scores['thinker'] += 1
        else:
            scores['explorer'] += 2
        
        # Question 8: Group settings scoring
        group_answer = response_dict.get(8, '')
        if group_answer == 'Take charge and lead':
            scores['leader'] += 3
        elif group_answer == 'Contribute ideas actively':
            scores['explorer'] += 1
            scores['leader'] += 1
        elif group_answer == 'Listen and support others':
            scores['nurturer'] += 3
        elif group_answer == 'Observe and analyze':
            scores['thinker'] += 3
        
        # Question 9: Daydreaming scoring
        daydream = response_dict.get(9, '')
        if daydream == 'yes':
            scores['explorer'] += 1
            scores['thinker'] += 1
        else:
            scores['leader'] += 1
        
        # Find the highest scoring personality type
        top_personality = max(scores, key=scores.get)
        personality_data = self.personality_types[top_personality].copy()
        personality_data['result_type'] = top_personality
        personality_data['scores'] = scores
        
        return personality_data