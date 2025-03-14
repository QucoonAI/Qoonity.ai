import api
import json
import requests
import github

applicationId = 290

token = "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"
repo_name = "test-repo4"
github_manager = github.GitHubManager(token)

#print("### Started")
#response = api.get_entity_by_application_id(api.login().get("token"), applicationId)
#print(json.dumps(response,indent=4))
    


#deploy = api.code_deploy(applicationId)
#print(deploy)



def download_and_push_code(application_id, application_name, github_manager):
    """
    Downloads code from S3 URL and pushes it to GitHub repository.
    
    Args:
        api: API client object
        application_id: ID of the application to download
        application_name: Name of the application/repository
        github_manager: GitHub manager object with push_zip_to_repo method
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Downloading and pushing code for application ID: {application_id}")
        # Get S3 download URL from API
        print("Getting download URL")
        api_response = api.code_s3_url(application_id)
        if not api_response or 's3Url' not in api_response:
            print("Failed to get download URL")
            return False
            
        # Download zip content directly
        response = requests.get(api_response['s3Url'])
        response.raise_for_status()
        zip_content = response.content
        
        # Push using GitHub manager
        success = github_manager.push_zip_to_repo(
            repo_owner="QuCoon-ML-AI",
            repo_name=application_name,
            zip_content=zip_content,
            commit_message=f"Initial commit for {application_name}"
        )
        
        return success
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    

download_and_push_code(application_id=applicationId, application_name=repo_name, github_manager=github_manager)

print("### Completed")