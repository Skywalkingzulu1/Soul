from github import Github
from soul.core.config import config
from soul.core.logger import setup_logger

logger = setup_logger(__name__)

class GitHubClient:
    """Native GitHub API client."""
    
    def __init__(self):
        if not config.github_token:
            logger.warning("GITHUB_TOKEN not found in environment.")
            self.gh = None
        else:
            self.gh = Github(config.github_token)

    def get_user_info(self):
        """Get authenticated user info."""
        if not self.gh: return None
        try:
            user = self.gh.get_user()
            return {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "repos_count": user.public_repos
            }
        except Exception as e:
            logger.error(f"Failed to get GitHub user info: {e}")
            return None

    def list_repos(self):
        """List repositories for the authenticated user."""
        if not self.gh: return []
        try:
            return [repo.full_name for repo in self.gh.get_user().get_repos()]
        except Exception as e:
            logger.error(f"Failed to list repositories: {e}")
            return []

    def create_issue(self, repo_name, title, body):
        """Create an issue in a repository."""
        if not self.gh: return False
        try:
            repo = self.gh.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body)
            logger.info(f"Created issue #{issue.number} in {repo_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            return False
