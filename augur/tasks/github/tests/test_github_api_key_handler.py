from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler

logger = logging.getLogger(__name__)

@pytest.fixture
def session():

    return DatabaseSession

def key_handler(session):

    return GithubApiKeyHandler(logger, session)

def test_github_api_key_handler_get_config_key(key_handler):

    pass