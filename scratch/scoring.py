import csv
import requests
import sys
import re
import ipdb

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# data = []
# with open('data.csv') as File:
#     reader = csv.DictReader(File)
#     for row in reader:
#         data.append(row)

repo_ids = [1, 25707, 25681, 25698, 25528, 25677, 25811, 25495, 25574, 25893, 25808, 25819, 25500, 25522, 25501, 25703, 25623, 25763, 25754, 25476, 25900, 25758, 25884, 25706, 25906, 25594, 25842, 25513, 25814, 1, 25570, 25502, 25647, 25876, 25841, 25462, 25537, 25532, 25614, 25600, 25593, 25470, 25459, 25454, 25465, 25479, 25468, 25455, 25458, 25456, 25478, 25457, 25477, 25453, 25471, 25800, 25833, 25672, 25615, 25490, 25786, 25556, 25549, 25697, 25526, 25921, 25782, 25521, 25599, 25474, 25438, 25674, 25686, 25692, 25904, 25895, 25689, 25582, 25590, 25642, 25802, 25646, 25484, 25604, 25817, 25696, 25510, 25473, 25780, 25850, 25460, 25871, 25889, 25825, 25858, 25691, 25920, 25503, 25567, 25678, 25762, 25777, 25683, 25452, 25565, 25857, 25926, 25597, 25481, 25624, 25602, 25520, 25612, 25924, 25745, 25799, 25598, 25564, 25670, 25828, 25861, 25488, 25515, 25872, 25665, 25661, 25491, 25504, 25849, 25641, 25629, 25580, 25592, 25776, 25451, 25756, 25757, 25434, 25589, 25475, 25701, 25563, 25472, 25533, 25911, 25907, 25449, 25552, 25628, 25891, 25558, 25896, 25860, 25892, 25467, 25651, 25912, 25667, 25652, 25886, 25787, 25431, 25688, 25531, 25854, 25445, 25550, 25699, 25804, 25542, 25673, 25785, 25752, 25791, 25587, 25664, 25806, 25905, 25619, 25620, 25581, 25505, 25918, 25832, 25916, 25506, 25635, 25658, 25663, 25662, 25656, 25660, 25659, 25657, 25655, 25653, 25669, 25666, 25496, 25524, 25915, 25517, 25492, 25770, 25919, 25897, 25807, 25631, 25637, 25608, 25740, 25749, 25741, 25718, 25710, 25726, 25714, 25725, 25724, 25723, 25722, 25742, 25721, 25720, 25719, 25727, 25739, 25746, 25743, 25738, 25737, 25736, 25734, 25744, 25712, 25713, 25717, 25747, 25748, 25733, 25735, 25715, 25731, 25716, 25730, 25732, 25729, 25728, 25543, 25695, 25601, 25555, 25668, 25883, 25442, 25694, 25583, 25705, 25810, 25815, 25493, 25494, 25461, 25572, 25605, 25622, 25616, 25617, 25638, 25632, 25609, 25613, 25927, 25610, 25831, 25852, 25855, 25469, 25463, 25466, 25644, 25750, 25682, 25573, 25835, 25433, 25759, 25577, 25880, 25498, 25816, 25625, 25559, 25766, 25769, 25767, 25774, 25881, 25489, 25436, 25448, 25634, 25846, 25798, 25562, 25538, 25450, 25853, 25561, 25539, 25535, 25753, 25781, 25621, 25611, 25569, 25687, 25887, 25869, 25675, 25859, 25823, 25704, 25803, 25507, 25865, 25862, 25870, 25867, 25868, 25874, 25866, 25864, 25863, 25885, 25709, 25607, 25584, 25626, 25575, 25925, 25917, 25586, 25554, 25760, 25784, 25432, 25643, 25898, 25909, 25894, 25899, 25534, 25778, 25840, 25837, 25844, 25843, 25838, 25848, 25856, 25851, 25443, 25648, 25645, 25680, 25901, 25497, 25516, 25603, 25630, 25654, 25464, 25795, 25761, 25783, 25548, 25499, 25483, 25751, 25512, 25834, 25518, 25519, 25553, 25700, 25650, 25444, 25447, 25711, 25446, 25486, 25529, 25511, 25797, 25809, 25606, 25875, 25551, 25545, 25779, 25557, 25560, 25482, 25547, 25508, 25913, 25801, 25914, 25830, 25679, 25525, 25805, 25839, 25827, 25826, 25813, 25812, 25821, 25820, 25579, 25595, 25596, 25618, 25755, 25788, 25790, 25789, 25794, 25792, 25793, 25796, 25910, 25768, 25566, 25546, 25585, 25487, 25873, 25877, 25775, 25536, 25922, 25923, 25576, 25509, 25435, 25485, 25649, 25530, 25671, 25818, 25690, 25633, 25636, 25888, 25627, 25847, 25829, 25591, 25702, 25845, 25708, 25480, 25822, 25882, 25836, 25903, 25685, 25540, 25639, 25773, 25527, 25878, 25693, 25541, 25568, 25588, 25684, 25676, 25514, 25890, 25879, 25544, 25439, 25764, 25640, 25772, 25430, 25578, 25571, 25902, 25523, 25440, 25824, 25441, 25437, 25771, 25908, 25765]
server_location = "http://localhost:5000/api/unstable/repos"

def calculate_watchers_score(repo_id):
    score = 0
    count = requests.get(f"{server_location}/{repo_id}/toss-repo-info").json()[0]['watchers']
    if count >= 2 and count <= 5:
        score = 1
    elif count >= 6 and count <= 15:
        score = 2
    elif count >= 16 and count <= 30:
        score = 3
    elif count >= 31 and count <= 50:
        score = 4
    elif count >= 51:
        score = 5
    return score

def calculate_forks_score(repo_id):
    score = 0
    count = requests.get(f"{server_location}/{repo_id}/toss-repo-info").json()[0]['forks']
    if count >= 1 and count <= 5:
        score = 1
    elif count >= 6 and count <= 15:
        score = 2
    elif count >= 16 and count <= 30:
        score = 3
    elif count >= 31 and count <= 50:
        score = 4
    elif count >= 51:
        score = 5
    return score

def calculate_stars_score(repo_id):
    score = 0
    count = requests.get(f"{server_location}/{repo_id}/toss-repo-info").json()[0]['stars']
    if count >= 1 and count <= 5:
        score = 1
    elif count >= 6 and count <= 15:
        score = 2
    elif count >= 16 and count <= 30:
        score = 3
    elif count >= 31 and count <= 50:
        score = 4
    elif count >= 51:
        score = 5
    return score

def calculate_code_of_conduct_score(repo_id):
    score = 0
    location = requests.get(f"{server_location}/{repo_id}/toss-repo-info").json()[0]['code_of_conduct_file']
    if location != None:
        score = 5
    return score

def calculate_license_file_score(repo_id):
    score = 0
    location = requests.get(f"{server_location}/{repo_id}/toss-repo-info").json()[0]['license_file']
    if location != None:
        score = 5
    return score

def calculate_good_first_issue(repo_id):
    score = 0
    repo_info = requests.get(f"{server_location}/{repo_id}/toss-repo-info").json()[0]

    label_url = f"{repo_info['repo_git']}/labels?per_page=100"

    labels = [re.sub(r"\ |\_|\-", "", label['name'].lower()) for label in requests.get(label_url).json()]

    if 'goodfirstissue' in labels:
        score = 5

    return score

def calculate_last_commit_score(repo_id):
    score = 0
    now = datetime.now()
    repo_last_updated_raw = requests.get(f"{server_location}/{repo_id}/toss-repo-info").json()[0]['last_updated']

    last_updated = datetime.strptime(repo_last_updated_raw, "%Y-%m-%dT%H:%M:%S.%fZ")

    months = relativedelta(now, last_updated).months

    if months >= 0 and months < 3:
        score = 5
    elif months >= 3 and months < 6:
        score = 4
    elif months >= 6 and months < 9:
        score = 3
    elif months >= 9 and months < 12:
        score = 2
    elif months >= 12 and months < 23:
        score = 1

    return score

def calculate_best_practices_score(repo_id):
    score = 0
    repo_info = requests.get(f"{server_location}/{repo_id}/toss-repo-info").json()[0]
    default_branch = repo_info['default_branch']
    repo_name = repo_info['repo_git'][29:]

    file_types = ["README.md", "CONTRIBUTING.md"]

    for file in file_types:
        readme_url = f"https://raw.githubusercontent.com/{repo_name}/{default_branch}/{file}"
        response = requests.get(readme_url)
        if response.ok is True:
            score += 5

    return score

def calculate_last_release_score(repo_id):
    return 0

# for repo in repo_ids[:5]:
#     print(repo, calculate_watchers_score(repo))

# for repo in repo_ids[:5]:
#     print(repo, calculate_forks_score(repo))

# for repo in repo_ids[:5]:
#     print(repo, calculate_stars_score(repo))

# for repo in repo_ids[:5]:
#     print(repo, calculate_code_of_conduct_score(repo))

# for repo in repo_ids[:5]:
#     print(repo, calculate_license_file_score(repo))

# for repo in repo_ids[:5]:
#     print(repo, calculate_good_first_issue(repo))

# for repo in repo_ids[:5]:
#     print(repo, calculate_last_commit_score(repo))

# for repo in repo_ids[:5]:
#     print(repo, calculate_best_practices_score(repo))
