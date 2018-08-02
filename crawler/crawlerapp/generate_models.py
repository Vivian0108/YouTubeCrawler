import os

import google.oauth2.credentials

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
#CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():
    #flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    #credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, developerKey="AIzaSyC485wtcaeL1yZrciuDWrliKSC74k8UODM")


def print_response(response):
    print(response)

# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.


def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title", where
        # "snippet" will be an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]

            # For properties that have array values, convert a name like
            # "snippet.tags[]" to snippet.tags, and set a flag to handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key) - 2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title", but the resource does
                # not yet have a "snippet" object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the next time through the
                # "for pa in range ..." loop, we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description", and the resource
                # already has a "snippet" object.
                ref = ref[key]
    return resource

# Remove keyword arguments that are not set


def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.iter():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def videos_list_by_id(client, **kwargs):
    # See full sample for function
    #kwargs = remove_empty_kwargs(**kwargs)

    response = client.videos().list(
        **kwargs
    ).execute()

    return response


def channels_list_by_id(client, **kwargs):
    # See full sample for function
    #kwargs = remove_empty_kwargs(**kwargs)

    response = client.channels().list(
        **kwargs
    ).execute()

    return response


def get_columns(columns):
    ret = ""
    for i in columns:
        ret += "\n\t" + str(i) + " = models.TextField(default=\"\")"
    return ret


# Sample python code for i18nLanguages.list

def i18n_languages_list(client, **kwargs):
    # See full sample for function
    #kwargs = remove_empty_kwargs(**kwargs)

    response = client.i18nLanguages().list(
        **kwargs
    ).execute()

    return response

def i18n_regions_list(client,**kwargs):
  # See full sample for function
  #kwargs = remove_empty_kwargs(**kwargs)

  response = client.i18nRegions().list(
    **kwargs
  ).execute()

  return response

def MakeFile(columns, name):
    filepath = os.getcwd()
    temp_path = "models.py"
    write_str = ('''
class ''' + name + '''(models.Model):''' + get_columns(columns))
    print(write_str)
    with open(temp_path, 'a') as f:
        f.write(write_str)
        f.close()
    print('Execution completed.')


def run_cmds():
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    #os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    client = get_authenticated_service()

    #resp = videos_list_by_id(client,
    #                         part='contentDetails,liveStreamingDetails,localizations,player,recordingDetails,snippet,statistics,status,topicDetails',
    #                         id='Ks-_Mh1QhMc')
    col = []
    #for item in resp['items']:
    #    for i in item.keys():
    #        col.append(i)
    #        print(str(i) + ": " + str(item[i]) + "\n\n\n")
    #MakeFile(col, "Video")

    #resp = channels_list_by_id(client,
    #                           part='brandingSettings,contentDetails,contentOwnerDetails,id,localizations,snippet,statistics,status,topicDetails',
    #                           id='UC_x5XG1OV2P6uZZ5FSM9Ttw')
    #newcol = []
    #for item in resp['items']:
    #    for i in item.keys():
    #        newcol.append(i)
    #        print(str(i) + ": " + str(item[i]) + "\n\n\n")
    #MakeFile(newcol, "Channel")

    resp = i18n_languages_list(client,
                        part='snippet',
                        hl='en_US')
    snippets = []
    for item in resp['items']:
        tup = (item['snippet']['hl'], item['snippet']['name'])
        snippets.append(tup)
    return snippets


def get_region_snippets():
    client = get_authenticated_service()
    col = []
    resp = i18n_regions_list(client, part = 'snippet', hl='en_US')
    snippets = []
    for item in resp['items']:
        tup = (item['snippet']['gl'],item['snippet']['name'])
        snippets.append(tup)
    return snippets
