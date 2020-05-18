# slidominator - the sli.do like automator v3.0
import requests
import sys

def print_help():
    print("Usage  : {0} EVENT_CODE COMMENT_ID NUMBER_OF_LIKES".format(script_name))
    print("Example: {0} 12345 18939973 3".format(script_name))
    quit()

def args_parser(args):
    if 'event_code' in args and len(args['event_code']) != 5:
        print("The event code must be 5 digits long.")
        raise IndexError
    elif 'question_id' in args and len(args['question_id']) != 8:
        print("The question id must be 8 digits long.")
        raise IndexError
    elif 'like_number' in args and args['like_number'] <= 0:
        print("The number of likes must be greater than 0.")
        raise IndexError
    elif 'statusCode' in args and args['statusCode'] == 404:
        print('The question was not found in this event:')
        print()
        print('Status Code: {}'.format(args['statusCode']))
        print('Error  Code: {}'.format(args['error']))
        print('    Message: {}'.format(args['message']))
        print()
        raise KeyboardInterrupt
    elif 'event_question_id' in args:
        return args['event_question_user_score']
    else:
        return args

def print_info(options):
    print()
    print('URL : {0}'.format(options['url']['app']))
    print('NAME: {0}'.format(options['name']))
    print('CODE: {0}'.format(options['code']))
    print('HASH: {0}'.format(options['hash']))
    print()

try:
    # name of the script
    script_name = sys.argv[0].split(sep='/')[-1]
    
    # quick start / debugging
    # event code
    sys.argv.insert(1, '66666')
    # question id
    sys.argv.insert(2, '18939973')
    # like number
    sys.argv.insert(3, 5)

    # parsing the command line arguments
    args = args_parser({'event_code':sys.argv[1],'question_id':sys.argv[2],'like_number':sys.argv[3]})
    event_code  = args['event_code']
    question_id = args['question_id']
    like_number = args['like_number']

    # extract data from the public API using only the user-friendly event code
    event_api_base_url = 'https://app.sli.do/api/v0.5/events'
    event_api_data     = requests.get('{0}?code={1}'.format(event_api_base_url, event_code)).json()[0]
    event_uuid         = event_api_data['uuid']

    # headers required by sli.do in order to compute the vote
    headers = {
        # doesn't really matter what's used as long as it's not empty.
        'X-Client-Id': 'FakeAssID',
        # same thing as above...
        'X-Slidoapp-Version': 'Mr. Pickles',
        # also required.
        'Authorization':''
    }
    # what actually likes / dislikes the question
    # needs to be zero (0) in case disliking
    data = {
        "score":1
    }

    # builds the url to the auth page from where we extract the Bearer token
    auth_path = 'auth'
    auth_url = '{0}/{1}/{2}'.format(event_api_base_url, event_uuid, auth_path)

    # builds the url to the questions page where we can like a specific questions based on the provided id
    questions_path = 'questions'
    question_like_url = '{0}/{1}/{2}/{3}/like'.format(event_api_base_url, event_uuid, questions_path, question_id)

    # prints information about the event
    print_info(event_api_data)

    # tries to like the comment
    likes = 0
    for like in range(like_number):

        # fetch the Bearer token
        auth_token = requests.post(auth_url).json()['access_token']

        # updating header with token
        headers['Authorization'] = 'Bearer {0}'.format(auth_token)

        # likes the question
        request = requests.post(question_like_url, headers=headers, data=data).json()

        # checks to see what happened when trying to like the question
        if args_parser(request) == 1:
            likes += 1;
            print('\r{0} likes given out of {1}'.format(likes, like_number), end='')

    print("\nDone! You're finally popular! :)")
    print("Check the event page to see how many likes your question has now.")

except IndexError:
    print_help()
except KeyboardInterrupt:
    print("Quitting...")
