# slidominator - the sli.do like automator v3.0
import requests
import sys
import random

def print_help():
    print("\nUsage  : {0} EVENT_CODE QUESTION_ID NUMBER_OF_LIKES".format(script_name))
    print("Example: {0} 12345 18939973 3\n".format(script_name))
    quit()

def args_parser(args):
    if 'event_code' in args and len(args['event_code']) not in range(3, 33):
            print('\nEvent code must 3 to 32 digits long\n')
            raise IndexError
    elif 'question_id' in args and len(args['question_id']) != 8:
        print("\nThe question id must be 8 digits long.\n")
        raise IndexError
    elif 'like_number' in args and args['like_number'] <= 0:
        print("\nThe number of likes must be greater than 0.\n")
        raise IndexError
    elif 'statusCode' in args:
        if args['statusCode'] == 404:
            print('\nThe question was not found in this event:\n')
        elif args['statusCode'] == 403:
            print('\nAccess to this event has been limited with a captcha.')
            print('Only humans (or Selenium, wink wink) can like questions now.')
            print('...but fear not, we\'re working on it! :)\n')
        print('Status Code: {}'.format(args['statusCode']))
        print('Error  Code: {}'.format(args['error']))
        print('    Message: {}\n'.format(args['message']))
        raise KeyboardInterrupt
    elif 'event_question_id' in args:
        return args['event_question_user_score']
    else:
        return args

# 15-digit client id present in the header of the request
def client_id_generator():
    client_id = []
    for x in range(15):
        numbers     = client_id.append(chr(random.randint(48, 57)))
        chars_upper = client_id.append(chr(random.randint(65, 90)))
        chars_lower = client_id.append(chr(random.randint(97, 122)))
    random.shuffle(client_id)
    client_id = ''.join(client_id)[:15]
    return client_id

def print_info(options):
    print("\nWelcome to slidominator.")
    print("Let's give that uninspired question a little push!\n")
    print('URL : {0}'.format(options['url']['app']))
    print('NAME: {0}'.format(options['name']))

try:
    # name of the script
    script_name = sys.argv[0].split(sep='/')[-1]

    # parsing the command line arguments
    args = args_parser({'event_code':sys.argv[1],'question_id':sys.argv[2],'like_number':int(sys.argv[3])})
    event_code  = args['event_code']
    question_id = args['question_id']
    like_number = args['like_number']

    # extract data from the public API using only the user-friendly event code
    event_api_base_url = 'https://app.sli.do/api/v0.5/events'
    try:
        event_api_data     = requests.get('{0}?code={1}'.format(event_api_base_url, event_code)).json()[0]
        event_uuid         = event_api_data['uuid']
    except:
        print("\nEvent not found.\n")
        raise IndexError

    # headers required by sli.do in order to compute the vote
    headers = {
        # to avoid raising suspicions, let's use something similar to what they expect
        'X-Client-Id': client_id_generator(),
        # same thing as above...
        'X-Slidoapp-Version': 'SlidoParticipantApp/6.23.0 (web)',
        # also required.
        'Authorization':''
    }
    # what actually likes / dislikes the question
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

        # tries fetch the Bearer token
        try:
            auth_token = requests.post(auth_url).json()['access_token']
        # if something bad happens, parse the response to know what's wrong
        except:
            args_parser(requests.post(auth_url).json())

        # updating header with token
        headers['Authorization'] = 'Bearer {0}'.format(auth_token)

        # likes the question
        request = requests.post(question_like_url, headers=headers, data=data).json()

        # checks to see what happened when trying to like the question
        if args_parser(request) == 1:
            likes += 1;
            print('\r{0} likes given out of {1}'.format(likes, like_number), end='')

    print("\n\nDone! You're finally popular! :)")
    print("Check the event page to see how many likes your question has now.\n")

except IndexError:
    print_help()
except KeyboardInterrupt:
    print("Quitting...\n")
