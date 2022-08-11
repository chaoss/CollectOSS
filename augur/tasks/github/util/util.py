

def remove_duplicate_dicts(data_list):

    return [dict(y) for y in set(tuple(x.items()) for x in data_list)]


# This function adds a key value pair to a list of dicts and returns the modified list of dicts back
def add_key_value_pair_to_list_of_dicts(data_list, key, value):

    for data in data_list:

        data[key] = value

    return data_list


def get_owner_repo(git_url):
    """ Gets the owner and repository names of a repository from a git url

    :param git_url: String, the git url of a repository
    :return: Tuple, includes the owner and repository names in that order
    """
    split = git_url.split('/')

    owner = split[-2]
    repo = split[-1]

    if '.git' == repo[-4:]:
        repo = repo[:-4]

    return owner, repo